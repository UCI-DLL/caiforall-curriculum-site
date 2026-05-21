from __future__ import annotations

import csv
import re
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

PAGES = [
    ("act1", "act-1.html", "ACT 1", "published", 1),
    ("act2", "act-2.html", "ACT 2", "published", 2),
    ("act3", "act-3.html", "ACT 3", "published", 3),
    ("act4", "act-4.html", "Coding+AI", "published", 4),
    ("scratch", "scratch-basics.html", "Scratch Basics", "published", 5),
]

HOMEPAGE_EXTRA = [
    {
        "curriculum_id": "science_inquiry_studio",
        "title": "Science+AI",
        "description": "A new curriculum pathway for science investigation, data-rich inquiry, and classroom-ready exploration.",
        "bullet_points": "",
        "status_label": "In development",
        "image_drive_url": "",
        "button_label": "",
        "display_order": "6",
    },
]


def text(node) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True) if node else "").strip()


def write_csv(name: str, fields: list[str], rows: list[dict[str, str]]) -> None:
    CONTENT.mkdir(exist_ok=True)
    with (CONTENT / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    curricula = []
    units = []
    lessons = []
    lesson_resources = []
    teacher_resources = []
    homepage_cards = []

    for curriculum_id, filename, quick_title, status, order in PAGES:
        soup = BeautifulSoup((ROOT / filename).read_text(encoding="utf-8"), "html.parser")
        heading = text(soup.select_one(".curriculum-hero h1"))
        title = heading.replace(" Curriculum", "")
        grade = text(soup.select_one(".hero-kicker")).replace(" curriculum", "")
        summary = text(soup.select_one(".curriculum-hero p"))
        first_img = soup.select_one(".unit-media img")
        cover = first_img.get("src", "") if first_img else ""
        curricula.append(
            {
                "id": curriculum_id,
                "title": title,
                "heading": heading,
                "grade_label": grade,
                "brief_description": summary,
                "slug": filename,
                "status": status,
                "cover_image_drive_url": cover,
                "display_order": str(order),
            }
        )
        homepage_cards.append(
            {
                "curriculum_id": curriculum_id,
                "title": title,
                "description": summary,
                "bullet_points": "",
                "status_label": "",
                "image_drive_url": cover,
                "button_label": f"Open {quick_title}",
                "display_order": str(order),
            }
        )

        for unit_index, unit in enumerate(soup.select(".unit-panel"), start=1):
            unit_id = f"unit-{unit_index}"
            image = unit.select_one(".unit-media img")
            objectives = "\n".join(text(li) for li in unit.select(".objectives li")) or text(unit.select_one(".objectives p"))
            units.append(
                {
                    "curriculum_id": curriculum_id,
                    "unit_id": unit_id,
                    "title": text(unit.select_one(".unit-main h2")),
                    "description": text(unit.select_one(".unit-overview")),
                    "objectives": objectives,
                    "image_drive_url": image.get("src", "") if image else "",
                    "display_order": str(unit_index),
                }
            )
            for resource_order, link in enumerate(unit.select(".unit-main > .unit-resource-row .resource-chip"), start=1):
                lesson_resources.append(
                    {
                        "curriculum_id": curriculum_id,
                        "unit_id": unit_id,
                        "lesson_id": "__unit__",
                        "label": text(link),
                        "url": link.get("href", ""),
                        "resource_type": "Unit Resource",
                        "display_order": str(resource_order),
                    }
                )
            for lesson_index, lesson in enumerate(unit.select(".lesson"), start=1):
                lesson_id = f"lesson-{lesson_index}"
                lessons.append(
                    {
                        "curriculum_id": curriculum_id,
                        "unit_id": unit_id,
                        "lesson_id": lesson_id,
                        "title": text(lesson.select_one(".lesson-summary")),
                        "description": "",
                        "objective_bullets": "|".join(text(li) for li in lesson.select(".lesson-objectives li")),
                        "duration": text(lesson.select_one(".duration")),
                        "display_order": str(lesson_index),
                    }
                )
                for resource_order, link in enumerate(lesson.select(".unit-resource-row .resource-chip"), start=1):
                    lesson_resources.append(
                        {
                            "curriculum_id": curriculum_id,
                            "unit_id": unit_id,
                            "lesson_id": lesson_id,
                            "label": text(link),
                            "url": link.get("href", ""),
                            "resource_type": "Lesson Resource",
                            "display_order": str(resource_order),
                        }
                    )

        for resource_order, link in enumerate(soup.select(".teacher-resources .quick-resources a"), start=1):
            teacher_resources.append(
                {
                    "curriculum_id": curriculum_id,
                    "label": text(link),
                    "url": link.get("href", ""),
                    "resource_type": "Resource",
                    "display_order": str(resource_order),
                }
            )

    homepage_cards.extend(HOMEPAGE_EXTRA)

    write_csv(
        "curricula.csv",
        ["id", "title", "heading", "grade_label", "brief_description", "slug", "status", "cover_image_drive_url", "display_order"],
        curricula,
    )
    write_csv("units.csv", ["curriculum_id", "unit_id", "title", "description", "objectives", "image_drive_url", "display_order"], units)
    write_csv("lessons.csv", ["curriculum_id", "unit_id", "lesson_id", "title", "description", "objective_bullets", "duration", "display_order"], lessons)
    write_csv(
        "lesson_resources.csv",
        ["curriculum_id", "unit_id", "lesson_id", "label", "url", "resource_type", "display_order"],
        lesson_resources,
    )
    write_csv("teacher_resources.csv", ["curriculum_id", "label", "url", "resource_type", "display_order"], teacher_resources)
    write_csv(
        "homepage_cards.csv",
        ["curriculum_id", "title", "description", "bullet_points", "status_label", "image_drive_url", "button_label", "display_order"],
        homepage_cards,
    )
    print(f"Wrote seed CSV content to {CONTENT}")


if __name__ == "__main__":
    main()
