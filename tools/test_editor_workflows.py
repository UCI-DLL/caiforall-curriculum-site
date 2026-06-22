from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from content_loader import ContentError, build_content, read_csv_tables
from build_refined_site import short_unit_title


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_from_rows(tables: dict[str, list[dict[str, str]]]):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        filenames = {
            "curricula": "curricula.csv",
            "units": "units.csv",
            "lessons": "lessons.csv",
            "lesson_resources": "lesson_resources.csv",
            "teacher_resources": "teacher_resources.csv",
            "homepage_cards": "homepage_cards.csv",
        }
        for table, filename in filenames.items():
            write_csv(root / filename, tables.get(table, [{}]))
        return build_content(read_csv_tables(root), resolve_images=False)


def base_tables() -> dict[str, list[dict[str, str]]]:
    return {
        "curricula": [
            {
                "curriculum_id": "act2",
                "navigation_title": "ACT 2: Scratch Design",
                "page_heading": "ACT 2: Scratch Design Curriculum",
                "grade_label": "5th Grade",
                "short_description": "Original ACT 2 description.",
                "page_filename": "act-2.html",
                "publish_status": "published",
                "display_order": "1",
                "image_asset_path": "curricula/act2/cover.png",
            }
        ],
        "units": [
            {
                "curriculum_id": "act2",
                "unit_id": "unit-1",
                "unit_title": "Unit 1: Animation",
                "unit_description": "Original unit description.",
                "learning_objectives": "Define sequence\nCreate an animation",
                "image_asset_path": "curricula/act2/units/unit-1-unit-1-animation.png",
                "display_order": "1",
            }
        ],
        "lessons": [
            {
                "curriculum_id": "act2",
                "unit_id": "unit-1",
                "lesson_id": "lesson-1",
                "lesson_title": "Lesson 1.1: Scratch Basics",
                "lesson_description": "Original lesson description.",
                "lesson_objective_bullets": "Review Scratch basics|Practice sequence and events",
                "lesson_duration": "50 minutes",
                "display_order": "1",
            }
        ],
        "lesson_resources": [
            {
                "curriculum_id": "act2",
                "unit_id": "unit-1",
                "lesson_id": "lesson-1",
                "link_label": "Lesson Plan",
                "resource_url": "https://example.com/lesson-plan",
                "resource_type": "Lesson Resource",
                "display_order": "1",
            }
        ],
        "teacher_resources": [
            {
                "curriculum_id": "act2",
                "link_label": "Teacher Guide",
                "resource_url": "https://example.com/teacher-guide",
                "resource_type": "Teacher Resource",
                "display_order": "1",
            }
        ],
        "homepage_cards": [
            {
                "curriculum_id": "act2",
                "card_title": "ACT 2: Scratch Design",
                "card_description": "Original homepage card.",
                "card_bullet_points": "5th Grade|Scratch|Animation",
                "status_label": "",
                "image_asset_path": "homepage/act2-card.png",
                "card_button_label": "Open ACT 2",
                "display_order": "1",
            }
        ],
    }


def test_change_descriptions() -> None:
    tables = base_tables()
    tables["curricula"][0]["short_description"] = "Updated curriculum description."
    tables["homepage_cards"][0]["card_description"] = "Updated homepage description."
    content = build_from_rows(tables)
    assert content.pages[0].summary == "Updated curriculum description."
    assert content.homepage_cards[0].description == "Updated homepage description."


def test_add_new_curriculum() -> None:
    tables = base_tables()
    tables["curricula"].append(
        {
            "curriculum_id": "test_remote",
            "navigation_title": "Test Remote",
            "page_heading": "Test Remote Curriculum",
            "grade_label": "Test Grade",
            "short_description": "A test curriculum used to confirm remote publishing.",
            "page_filename": "test-remote.html",
            "publish_status": "published",
            "display_order": "2",
            "image_asset_path": "homepage/smile.webp",
        }
    )
    tables["units"].append(
        {
            "curriculum_id": "test_remote",
            "unit_id": "unit-1",
            "unit_title": "Unit 1: Test Unit",
            "unit_description": "This unit confirms that a new curriculum page can be published remotely.",
            "learning_objectives": "Confirm the page renders\nConfirm the unit appears",
            "image_asset_path": "homepage/smile.webp",
            "display_order": "1",
        }
    )
    tables["lessons"].append(
        {
            "curriculum_id": "test_remote",
            "unit_id": "unit-1",
            "lesson_id": "lesson-1",
            "lesson_title": "Lesson 1: Test Lesson",
            "lesson_description": "This lesson confirms that accordions render correctly.",
            "lesson_objective_bullets": "Confirm the accordion renders|Review generated content",
            "lesson_duration": "10 minutes",
            "display_order": "1",
        }
    )
    tables["homepage_cards"].append(
        {
            "curriculum_id": "test_remote",
            "card_title": "Test Remote",
            "card_description": "A temporary card for testing remote publishing.",
            "card_bullet_points": "Test Grade|Remote publishing|Validation",
            "status_label": "",
            "image_asset_path": "homepage/smile.webp",
            "card_button_label": "Open Test Remote",
            "display_order": "2",
        }
    )
    content = build_from_rows(tables)
    page = next(page for page in content.pages if page.id == "test_remote")
    card = next(card for card in content.homepage_cards if card.curriculum_id == "test_remote")
    assert page.file == "test-remote.html"
    assert page.units[0].lessons[0].title == "Lesson 1: Test Lesson"
    assert card.page is page


def test_add_unit_and_resource() -> None:
    tables = base_tables()
    tables["units"].append(
        {
            "curriculum_id": "act2",
            "unit_id": "unit-2",
            "unit_title": "Unit 2: Extension Project",
            "unit_description": "Students extend their Scratch design work.",
            "learning_objectives": "Plan a project\nBuild and test",
            "image_asset_path": "homepage/smile.webp",
            "display_order": "2",
        }
    )
    tables["lessons"].append(
        {
            "curriculum_id": "act2",
            "unit_id": "unit-2",
            "lesson_id": "lesson-1",
            "lesson_title": "Lesson 2.1: Plan",
            "lesson_description": "Students plan their project.",
            "lesson_objective_bullets": "Plan a project",
            "lesson_duration": "45 minutes",
            "display_order": "1",
        }
    )
    tables["lesson_resources"].append(
        {
            "curriculum_id": "act2",
            "unit_id": "unit-2",
            "lesson_id": "__unit__",
            "link_label": "Unit Overview",
            "resource_url": "https://example.com/unit-overview",
            "resource_type": "Unit Resource",
            "display_order": "1",
        }
    )
    content = build_from_rows(tables)
    page = content.pages[0]
    assert len(page.units) == 2
    assert page.units[1].links[0].label == "Unit Overview"


def test_invalid_status_is_caught() -> None:
    tables = base_tables()
    tables["curricula"][0]["publish_status"] = "draft maybe"
    try:
        build_from_rows(tables)
    except ContentError as exc:
        assert "status must be 'published', 'development', or 'hidden'" in str(exc)
    else:
        raise AssertionError("Invalid status should fail validation.")


def test_unit_letter_suffix_is_preserved() -> None:
    assert short_unit_title("Unit 5A: Advanced AI Apps") == "Unit 5A"
    assert short_unit_title("Unit 5B: Agentic Coding Tools") == "Unit 5B"


def main() -> None:
    tests = [
        test_change_descriptions,
        test_add_new_curriculum,
        test_add_unit_and_resource,
        test_invalid_status_is_caught,
        test_unit_letter_suffix_is_preserved,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
