from __future__ import annotations

import sys

from content_loader import ContentError, load_content


def main() -> None:
    try:
        content = load_content(resolve_images=False)
    except ContentError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)
    page_count = len([page for page in content.pages if page.status.lower() == "published"])
    unit_count = sum(len(page.units) for page in content.pages)
    lesson_count = sum(len(unit.lessons) for page in content.pages for unit in page.units)
    print(f"Content valid: {page_count} published curricula, {unit_count} units, {lesson_count} lessons, {len(content.homepage_cards)} homepage cards.")


if __name__ == "__main__":
    main()
