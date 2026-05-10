from __future__ import annotations

import os
import sys

from content_loader import ContentError, drive_image_resolver, read_csv_tables, read_google_tables


IMAGE_TABLES = {
    "curricula": "cover_image_drive_url",
    "units": "image_drive_url",
    "homepage_cards": "image_drive_url",
}


def load_tables() -> dict[str, list[dict[str, str]]]:
    source = os.environ.get("CONTENT_SOURCE", "csv")
    if source == "google":
        return read_google_tables()
    if source == "csv":
        return read_csv_tables()
    raise ContentError("CONTENT_SOURCE must be 'csv' or 'google'.")


def main() -> None:
    resolver = drive_image_resolver()
    if not resolver.configured():
        raise SystemExit("Set GOOGLE_DRIVE_IMAGE_ROOT_ID before checking Drive image paths.")

    try:
        tables = load_tables()
        checked = 0
        for table, url_column in IMAGE_TABLES.items():
            for index, row in enumerate(tables.get(table, []), start=2):
                asset_path = row.get("image_asset_path", "").strip()
                if not asset_path:
                    continue
                resolver.file_id_for_path(asset_path)
                checked += 1
        print(f"Drive image paths valid: {checked} image_asset_path values resolved.")
    except ContentError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
