# Content Editor Handbook

This handbook explains how to update the Computing & AI for All Curriculum website without editing code.

The website content comes from two places:

- **Google Sheets**: text, page structure, lessons, and links
- **Google Drive**: images

After editing, a reviewer publishes from GitHub:

```text
GitHub repository -> Actions -> Publish Website -> Run workflow
```

If something is wrong, GitHub will show an error message. If everything is valid, the public website updates.

## Quick Mental Model

Use this rule:

```text
Homepage Cards = what appears on the homepage
Curriculum Pages = which curriculum pages exist
Units = the unit tabs/blocks inside a curriculum page
Lessons = the lesson accordions inside a unit
Lesson Links = buttons inside lessons or unit summaries
Resource Links = resource buttons below a curriculum page
```

Most edits happen in only one or two tabs.

## Sheet Tabs

The recommended tab names are:

- `Curriculum Pages`
- `Units`
- `Lessons`
- `Lesson Links`
- `Resource Links`
- `Homepage Cards`

Older technical tab names, such as `curricula` and `lesson_resources`, still work, but the names above are easier for editors.

## Shared Image Folder

Images live in the shared Google Drive folder uploaded from `content/drive-image-library`.

Use paths like these in the Sheet:

```text
homepage/act2-card.png
curricula/act2/cover.png
curricula/act2/units/unit-1-unit-1-animation.png
```

Do not paste Google Drive image URLs into the Sheet. Use the file path inside the shared image folder.

## Tab 1: Curriculum Pages

One row creates one curriculum page.

Recommended columns:

```text
curriculum_id
navigation_title
page_heading
grade_label
short_description
page_filename
publish_status
display_order
image_asset_path
```

Example:

```text
curriculum_id: act2
navigation_title: ACT 2: Scratch Design
page_heading: ACT 2: Scratch Design
grade_label: 5th Grade
short_description: Fifth-grade Scratch lessons focused on animation, loops, games, and computational design.
page_filename: act-2.html
publish_status: published
display_order: 2
image_asset_path: curricula/act2/cover.png
```

Rules:

- `curriculum_id` must be short, stable, lowercase, and unique.
- `page_filename` must end in `.html`.
- `publish_status` must be `published` or `hidden`.
- A published page needs at least one matching row in `Units` to show useful content.
- Adding a row here does not automatically add a homepage card. Use `Homepage Cards` for that.

## Tab 2: Units

One row creates one unit tab/block inside a curriculum page.

Recommended columns:

```text
curriculum_id
unit_id
unit_title
unit_description
learning_objectives
display_order
image_asset_path
```

Example:

```text
curriculum_id: act2
unit_id: unit-1
unit_title: Unit 1: Animation
unit_description: Students review Scratch basics and create an animated story using sequence, events, and loops.
learning_objectives:
  Define sequence, event, and loop
  Modify an existing animation project
  Create an animated story in Scratch
display_order: 1
image_asset_path: curricula/act2/units/unit-1-unit-1-animation.png
```

Rules:

- `curriculum_id` must match a row in `Curriculum Pages`.
- `unit_id` must be unique within that curriculum.
- `unit_description` is shown below the unit title on the curriculum page.
- `learning_objectives` is kept for source/reference content.

## Tab 3: Lessons

One row creates one lesson accordion inside a unit.

Recommended columns:

```text
curriculum_id
unit_id
lesson_id
lesson_title
lesson_description
objective_bullets
lesson_duration
display_order
```

Example:

```text
curriculum_id: act2
unit_id: unit-1
lesson_id: lesson-1
lesson_title: Lesson 1.1: Scratch Basics, Sequence and Events Review
lesson_description: Students review Scratch basics and the CS concepts of sequence and event.
objective_bullets: Review Scratch basics|Practice sequence and events
lesson_duration: 50 minutes
display_order: 1
```

Rules:

- `curriculum_id` must match a curriculum page.
- `unit_id` must match a unit in that curriculum.
- `lesson_id` must be unique within that unit.
- `lesson_description` preserves the original lesson description in the sheet.
- `objective_bullets` is shown inside the lesson accordion under `Learning Objectives`. Separate bullets with `|`.
- Write each objective as a concise action phrase, such as `Introduce Scratch basics`, `Practice sequence and events`, or `Build an interactive project`. Avoid future-tense sentence framing.

## Tab 4: Lesson Links

One row creates one resource button.

Recommended columns:

```text
curriculum_id
unit_id
lesson_id
link_label
resource_url
resource_type
display_order
```

Example lesson-level link:

```text
curriculum_id: act2
unit_id: unit-1
lesson_id: lesson-1
link_label: Lesson Plan
resource_url: https://docs.google.com/document/d/example/edit
resource_type: Lesson Resource
display_order: 1
```

Example unit-level link:

```text
curriculum_id: act2
unit_id: unit-1
lesson_id: __unit__
link_label: Unit Overview
resource_url: https://docs.google.com/document/d/example/edit
resource_type: Unit Resource
display_order: 1
```

Rules:

- Use `lesson_id = __unit__` for a button near the unit description.
- Use a real lesson id for a button inside a lesson.
- Use `lesson_id = __unit__` and `link_label = Teacher Manual` when a unit needs a Teacher Manual accordion.
- Resource labels containing `Español`, `Espanol`, or `Spanish` appear on a separate line.
- `resource_url` must start with `http://` or `https://`.

## Tab 5: Resource Links

One row creates one curriculum-level resource button below the curriculum browser.

Recommended columns:

```text
curriculum_id
link_label
resource_url
resource_type
display_order
```

Example:

```text
curriculum_id: act2
link_label: Lesson Plans
resource_url: https://drive.google.com/drive/folders/example
resource_type: Resource
display_order: 1
```

Do not add `CreatiCode Platform`, `Give Feedback`, `Give Feedback Form`, or `Feedback Form` to this tab. These links are filtered out when the site is built.

## Tab 6: Homepage Cards

One row creates one homepage card.

Recommended columns:

```text
curriculum_id
card_title
card_description
card_bullet_points
status_label
image_asset_path
card_button_label
display_order
```

Example card for a published curriculum:

```text
curriculum_id: act2
card_title: ACT 2: Scratch Design
card_description: Fifth-grade Scratch lessons focused on animation, loops, games, and computational design.
card_bullet_points: 5th Grade|Scratch|Animation and games
status_label:
image_asset_path: homepage/act2-card.png
card_button_label: Open ACT 2
display_order: 2
```

Example upcoming card:

```text
curriculum_id: science_inquiry_studio
card_title: Science Inquiry Studio
card_description: A new pathway for science investigation and data-rich classroom inquiry.
card_bullet_points:
status_label: In development
image_asset_path: homepage/smile.webp
card_button_label:
display_order: 6
```

Rules:

- If the card should open a curriculum page, `curriculum_id` must match a `published` row in `Curriculum Pages`, and `card_button_label` should be filled.
- If the card is only a future/coming-soon card, use `status_label`, such as `In development`, and leave `card_button_label` blank.

## Workflow 1: Change a Description

Goal: update the description on an existing curriculum page.

1. Open the `Curriculum Pages` tab.
2. Find the row, such as `act2`.
3. Edit `short_description`.
4. Ask the reviewer to publish.

Expected result:

- The curriculum page hero description changes.
- The homepage card does not change unless you also edit `Homepage Cards.card_description`.

## Workflow 2: Change a Homepage Card

Goal: update the text shown on the homepage.

1. Open `Homepage Cards`.
2. Find the row, such as `act2`.
3. Edit `card_description`.
4. Ask the reviewer to publish.

Expected result:

- Only the homepage card text changes.

## Workflow 3: Replace an Image

Goal: replace the ACT 2 homepage card image.

1. Open the shared Google Drive image folder.
2. Go to `homepage/`.
3. Replace or upload the image file.
4. Use a clear file name, such as `act2-card-2026.png`.
5. Open `Homepage Cards`.
6. Update `image_asset_path`:

```text
homepage/act2-card-2026.png
```

7. Ask the reviewer to publish.

Expected result:

- GitHub validates that the image path exists.
- The build downloads the image into `assets/generated-images/`.
- The public site displays the new image.

## Workflow 4: Add a New Published Curriculum

Goal: add a new curriculum page and homepage card.

### Step A: Add a curriculum page

Add a row in `Curriculum Pages`:

```text
curriculum_id: test_remote
navigation_title: Test Remote
page_heading: Test Remote
grade_label: Test Grade
short_description: A test curriculum used to confirm remote publishing.
page_filename: test-remote.html
publish_status: published
display_order: 6
image_asset_path: homepage/smile.webp
```

### Step B: Add at least one unit

Add a row in `Units`:

```text
curriculum_id: test_remote
unit_id: unit-1
unit_title: Unit 1: Test Unit
unit_description: This unit confirms that a new curriculum page can be published remotely.
learning_objectives:
  Confirm the page renders
  Confirm the unit appears
display_order: 1
image_asset_path: homepage/smile.webp
```

### Step C: Add at least one lesson

Add a row in `Lessons`:

```text
curriculum_id: test_remote
unit_id: unit-1
lesson_id: lesson-1
lesson_title: Lesson 1: Test Lesson
lesson_description: This lesson confirms that accordions render correctly.
objective_bullets: Confirm the accordion renders|Review generated content
lesson_duration: 10 minutes
display_order: 1
```

### Step D: Add a homepage card

Add a row in `Homepage Cards`:

```text
curriculum_id: test_remote
card_title: Test Remote
card_description: A temporary card for testing remote publishing.
status_label:
image_asset_path: homepage/smile.webp
card_button_label: Open Test Remote
display_order: 8
```

Expected result:

- A new page `test-remote.html` is generated.
- The homepage shows a new Test Remote card.
- The card button opens the new page.
- The curriculum dropdown includes Test Remote.

## Workflow 5: Add a Unit to an Existing Curriculum

Goal: add a new unit to ACT 2.

1. Open `Units`.
2. Add a row:

```text
curriculum_id: act2
unit_id: unit-5
unit_title: Unit 5: Extension Project
unit_description: Students extend their Scratch design work with an independent project.
learning_objectives:
  Plan a project
  Build and test an interactive Scratch artifact
display_order: 5
image_asset_path: homepage/smile.webp
```

3. Add at least one matching row in `Lessons`.
4. Ask the reviewer to publish.

Expected result:

- ACT 2 gets a new Unit 5 tab.
- Clicking Unit 5 shows the new unit and lessons.

## Workflow 6: Add a Lesson Resource Link

Goal: add a slide deck button to one lesson.

1. Open `Lesson Links`.
2. Add a row:

```text
curriculum_id: act2
unit_id: unit-1
lesson_id: lesson-1
link_label: Slide Deck
resource_url: https://docs.google.com/presentation/d/example/edit
resource_type: Lesson Resource
display_order: 2
```

Expected result:

- The lesson accordion shows a new `Slide Deck` button.

## Common Validation Errors

`status must be 'published' or 'hidden'`

Fix `Curriculum Pages.publish_status`.

`slug must be an .html filename`

Fix `Curriculum Pages.page_filename`. Example: `test-remote.html`.

`unit_id does not exist`

The lesson or link references a unit that does not exist in `Units`.

`lesson_id does not exist`

The lesson link references a lesson that does not exist in `Lessons`.

`button_label requires curriculum_id to be a published curriculum`

The homepage card has a button, but the curriculum page is missing or not published.

`Could not find image asset`

The `image_asset_path` does not match a file in the shared Google Drive image folder. Check spelling, folder, and file extension.

## Publishing

After editing:

1. Open GitHub.
2. Go to the website repository.
3. Click `Actions`.
4. Click `Publish Website`.
5. Click `Run workflow`.
6. Wait for the green check.

If it fails, open the failed step and read the error. Most errors point to the exact tab and row number.
