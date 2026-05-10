from __future__ import annotations

import csv
import mimetypes
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests

from build_refined_site import FALLBACK_LOGO
from content_loader import ContentError, HomeCard, Image, Page, Unit, load_content


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "content" / "drive-image-library"
MANIFEST_FILE = OUTPUT_DIR / "image-manifest.csv"


@dataclass(frozen=True)
class ImageAsset:
    source_url: str
    local_path: Path
    sheet_tab: str
    row_hint: str
    sheet_column: str
    suggested_drive_folder: str


def slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "image"


def extension_from_url(url: str, content_type: str = "") -> str:
    path = urlparse(url).path
    match = re.search(r"\.(png|jpe?g|gif|webp|svg)(?:$|[~._-])", path, re.I)
    if match:
        ext = match.group(1).lower()
        return ".jpg" if ext == "jpeg" else f".{ext}"
    guessed = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) if content_type else None
    if guessed in {".jpe", ".jpeg"}:
        return ".jpg"
    return guessed or ".jpg"


def add_image(
    assets: list[ImageAsset],
    image: Image | None,
    local_path_without_ext: Path,
    sheet_tab: str,
    row_hint: str,
    sheet_column: str,
    suggested_drive_folder: str,
) -> None:
    if not image or not image.src:
        return
    assets.append(
        ImageAsset(
            source_url=image.src,
            local_path=local_path_without_ext,
            sheet_tab=sheet_tab,
            row_hint=row_hint,
            sheet_column=sheet_column,
            suggested_drive_folder=suggested_drive_folder,
        )
    )


def collect_assets() -> list[ImageAsset]:
    content = load_content()
    assets: list[ImageAsset] = [
        ImageAsset(
            source_url=FALLBACK_LOGO,
            local_path=Path("site") / "logo",
            sheet_tab="site",
            row_hint="navigation logo",
            sheet_column="LOGO in tools/build_refined_site.py",
            suggested_drive_folder="CAIforALL Curriculum Images/site",
        )
    ]

    for card in content.homepage_cards:
        name = slug(card.curriculum_id or card.title)
        add_image(
            assets,
            card.image,
            Path("homepage") / f"{name}-card",
            "homepage_cards",
            card.curriculum_id or card.title,
            "image_drive_url",
            "CAIforALL Curriculum Images/homepage",
        )

    for page in content.pages:
        curriculum_folder = slug(page.id)
        add_image(
            assets,
            page.cover_image,
            Path("curricula") / curriculum_folder / "cover",
            "curricula",
            page.id,
            "cover_image_drive_url",
            f"CAIforALL Curriculum Images/curricula/{curriculum_folder}",
        )
        for unit in page.units:
            unit_folder = slug(unit.id)
            add_image(
                assets,
                unit.image,
                Path("curricula") / curriculum_folder / "units" / f"{unit_folder}-{slug(unit.title)[:44]}",
                "units",
                f"{page.id} / {unit.id}",
                "image_drive_url",
                f"CAIforALL Curriculum Images/curricula/{curriculum_folder}/units",
            )

    return assets


def download(asset: ImageAsset) -> tuple[Path, str]:
    if not asset.source_url.startswith(("http://", "https://")):
        return asset.local_path, "local"
    response = requests.get(asset.source_url, timeout=30)
    response.raise_for_status()
    ext = extension_from_url(asset.source_url, response.headers.get("content-type", ""))
    relative_path = asset.local_path.with_suffix(ext)
    output_path = OUTPUT_DIR / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)
    return relative_path, response.headers.get("content-type", "")


def main() -> None:
    try:
        assets = collect_assets()
    except ContentError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    failures = 0
    for asset in assets:
        try:
            relative_path, content_type = download(asset)
            print(f"Downloaded {relative_path}")
        except Exception as exc:
            failures += 1
            relative_path = asset.local_path
            content_type = ""
            print(f"FAILED {asset.source_url}: {exc}", file=sys.stderr)
        rows.append(
            {
                "local_file": str(relative_path),
                "source_url": asset.source_url,
                "sheet_tab": asset.sheet_tab,
                "row_hint": asset.row_hint,
                "sheet_column": asset.sheet_column,
                "suggested_drive_folder": asset.suggested_drive_folder,
                "content_type": content_type,
            }
        )

    with MANIFEST_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "local_file",
                "source_url",
                "sheet_tab",
                "row_hint",
                "sheet_column",
                "suggested_drive_folder",
                "content_type",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {MANIFEST_FILE.relative_to(ROOT)}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
