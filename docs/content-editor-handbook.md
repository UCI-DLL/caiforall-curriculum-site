# Content Editor Handbook

This handbook explains how to update the Computing and AI for All Curriculum website with Google Sheets, Google Drive images, and GitHub Actions.

The editor makes the content change, runs the publishing workflow, and checks the public website. The website layout, colors, and interaction design are controlled by the codebase. Editors only change structured content and image files.

```text
Edit Google Sheet and/or Google Drive images
Run GitHub Actions > Publish Website > Run workflow
Check the public website
```

## Core Editing Rules

These rules keep the website predictable. Follow them for every content update, even for small edits.

1. Edit only the existing Sheet tabs listed in this handbook.
2. Do not rename Sheet tabs.
3. Do not add new tabs for routine edits.
4. Do not paste Google Drive share links into image fields.
5. Use image file paths such as `homepage/act2-card.png`.
6. Run `Publish Website` after editing content or images.
7. Check the public website after the workflow finishes.

## Required Sheet Tabs

The Google Sheet tab names must exactly match the CSV file names used by the website. The website reads these exact names.

| Tab name | Purpose |
|---|---|
| `curricula` | Creates curriculum pages and curriculum navigation entries. |
| `units` | Creates unit tabs/blocks inside curriculum pages. |
| `lessons` | Creates lesson accordions inside units. |
| `lesson_resources` | Creates lesson-level and unit-level resource buttons. |
| `teacher_resources` | Creates curriculum-level resource buttons below the unit browser. |
| `homepage_cards` | Creates cards on the homepage. |

New units, lessons, links, homepage cards, and images are added as new rows in the existing tabs.

A new tab is allowed only when the website needs a new type of structured content that does not fit the current tabs. That requires a code update before the website can read it. A new curriculum page does not need a new tab; it needs new rows in the existing tabs.

## Image File Paths

Images are stored in the shared Google Drive image folder. The Sheet uses file paths relative to that folder.

For example, if an image is placed in the Drive folder like this:

```text
drive-image-library/homepage/data-stories-card.png
```

the Sheet value must be:

```text
homepage/data-stories-card.png
```

Common image path examples:

| Image use | Example `image_asset_path` |
|---|---|
| Homepage card image | `homepage/act2-card.png` |
| Curriculum cover image | `curricula/act2/cover.png` |
| Unit image | `curricula/act2/units/unit-1-animation.png` |
| Shared temporary image | `homepage/smile.webp` |

The path must match the folder name, file name, and extension exactly. `act2-card.png`, `act2-card.PNG`, and `act2-card-2026.png` are different file names.

## Tab Protocol: `curricula`

Use `curricula` for curriculum pages. One row creates one page and one navigation entry.

Required columns:

| Column | Required value |
|---|---|
| `id` | Stable unique curriculum id, lowercase, no spaces. Example: `act2`. |
| `title` | Navigation/card title. Example: `ACT 2: Scratch Design`. |
| `heading` | Page hero heading. Example: `ACT 2: Scratch Design`. |
| `grade_label` | Short grade/category label. Example: `5th Grade`. |
| `brief_description` | Short page description shown in the curriculum hero. |
| `slug` | Page filename ending in `.html`. Example: `act-2.html`. |
| `status` | Use only `published` or `hidden`. |
| `display_order` | Number used for sorting. |
| `image_asset_path` | Image file path in the shared Drive image folder. |

Example row:

| id | title | heading | grade_label | brief_description | slug | status | display_order | image_asset_path |
|---|---|---|---|---|---|---|---:|---|
| `data-stories` | `Data Stories` | `Data Stories Curriculum` | `Middle School` | `Students investigate data, build visual explanations, and communicate findings through interactive projects.` | `data-stories.html` | `published` | `6` | `curricula/data-stories/cover.png` |

Rules:

1. `status` must be exactly `published` or `hidden`.
2. `slug` must end in `.html`.
3. A published curriculum page needs at least one matching row in `units`.
4. A row in `curricula` does not create a homepage card. Use `homepage_cards` for homepage cards.

## Tab Protocol: `units`

Use `units` for the unit browser inside each curriculum page. One row creates one unit tab and one unit content block.

Required columns:

| Column | Required value |
|---|---|
| `curriculum_id` | Must match `curricula.id`. |
| `unit_id` | Stable unit id inside that curriculum. Example: `unit-1`. |
| `title` | Unit title shown on the page. |
| `description` | Unit overview text. |
| `objectives` | Source/reference learning objectives. |
| `display_order` | Number used for sorting within the curriculum. |
| `image_asset_path` | Unit image file path. |

Example row:

| curriculum_id | unit_id | title | description | objectives | display_order | image_asset_path |
|---|---|---|---|---|---:|---|
| `data-stories` | `unit-1` | `Unit 1: Asking Questions With Data` | `Students learn how to ask investigable questions, inspect a dataset, and identify patterns worth explaining.` | `Define a data question\nIdentify variables\nDescribe an initial pattern` | `1` | `curricula/data-stories/units/unit-1-asking-questions.png` |

Rules:

1. `curriculum_id` must already exist in `curricula`.
2. `unit_id` must be unique within the curriculum.
3. Use new rows for new units.
4. Do not create a separate tab for a new unit.

## Tab Protocol: `lessons`

Use `lessons` for lesson accordions inside each unit. One row creates one lesson.

Required columns:

| Column | Required value |
|---|---|
| `curriculum_id` | Must match `curricula.id`. |
| `unit_id` | Must match `units.unit_id` for that curriculum. |
| `lesson_id` | Stable lesson id inside that unit. Example: `lesson-1`. |
| `title` | Lesson title shown in the accordion. |
| `description` | Lesson description stored in the Sheet. |
| `objective_bullets` | Objectives shown in the lesson accordion, separated with `|`. |
| `duration` | Lesson duration. Example: `50 minutes`. |
| `display_order` | Number used for sorting within the unit. |

Example row:

| curriculum_id | unit_id | lesson_id | title | description | objective_bullets | duration | display_order |
|---|---|---|---|---|---|---|---:|
| `data-stories` | `unit-1` | `lesson-1` | `Lesson 1.1: What Makes a Good Data Question?` | `Students compare sample questions and revise them into questions that can be investigated with data.` | `Compare question types|Revise a data question|Explain what makes a question investigable` | `45 minutes` | `1` |

Rules:

1. `objective_bullets` uses `|` between bullet items.
2. Keep each objective concise and action-focused.
3. Use new rows for new lessons.
4. Do not create a separate tab for a new lesson.

## Tab Protocol: `lesson_resources`

Use `lesson_resources` for buttons connected to units and lessons. One row creates one resource button.

Required columns:

| Column | Required value |
|---|---|
| `curriculum_id` | Must match `curricula.id`. |
| `unit_id` | Must match a unit in that curriculum. |
| `lesson_id` | Use a lesson id, or use `__unit__` for a unit-level resource. |
| `label` | Button text. |
| `url` | Full resource URL beginning with `http://` or `https://`. |
| `resource_type` | Resource category. Example: `Lesson Resource`. |
| `display_order` | Number used for sorting. |

Example lesson-level row:

| curriculum_id | unit_id | lesson_id | label | url | resource_type | display_order |
|---|---|---|---|---|---|---:|
| `data-stories` | `unit-1` | `lesson-1` | `Lesson Plan` | `https://docs.google.com/document/d/example/edit` | `Lesson Resource` | `1` |

Example unit-level row:

| curriculum_id | unit_id | lesson_id | label | url | resource_type | display_order |
|---|---|---|---|---|---|---:|
| `data-stories` | `unit-1` | `__unit__` | `Unit Overview` | `https://docs.google.com/document/d/example/edit` | `Unit Resource` | `1` |

Rules:

1. Use `lesson_id = __unit__` for resources shown near the unit description.
2. Use a real `lesson_id` for resources shown inside a lesson accordion.
3. Resource labels containing `Español`, `Espanol`, or `Spanish` display on a separate resource row.
4. `url` must begin with `http://` or `https://`.

## Tab Protocol: `teacher_resources`

Use `teacher_resources` for curriculum-level links below the unit browser.

Required columns:

| Column | Required value |
|---|---|
| `curriculum_id` | Must match `curricula.id`. |
| `label` | Button text. |
| `url` | Full resource URL beginning with `http://` or `https://`. |
| `resource_type` | Resource category. Example: `Resource`. |
| `display_order` | Number used for sorting. |

Example row:

| curriculum_id | label | url | resource_type | display_order |
|---|---|---|---|---:|
| `data-stories` | `Lesson Plans` | `https://drive.google.com/drive/folders/example` | `Resource` | `1` |

Rules:

1. Do not add `CreatiCode Platform`, `Give Feedback`, `Give Feedback Form`, or `Feedback Form` to this tab.
2. These labels are filtered from the website output.

## Tab Protocol: `homepage_cards`

Use `homepage_cards` for homepage curriculum cards. A homepage card is separate from a curriculum page.

Required columns:

| Column | Required value |
|---|---|
| `curriculum_id` | Matches `curricula.id` for published cards, or a future id for upcoming cards. |
| `title` | Card title shown on the homepage. |
| `description` | Card description shown on the homepage. |
| `card_bullet_points` | Optional bullets separated with `|`. |
| `status_label` | Empty for live cards. Use text like `In development` for upcoming cards. |
| `image_asset_path` | Homepage image file path. |
| `button_label` | Button text for live cards. Empty for upcoming cards. |
| `display_order` | Number used for sorting. |

Example live card:

| curriculum_id | title | description | card_bullet_points | status_label | image_asset_path | button_label | display_order |
|---|---|---|---|---|---|---|---:|
| `data-stories` | `Data Stories` | `A middle-school pathway for data investigation, visual explanation, and interactive storytelling.` | `Middle School|Data literacy|Interactive storytelling` |  | `homepage/data-stories-card.png` | `Open Data Stories` | `6` |

Example upcoming card:

| curriculum_id | title | description | card_bullet_points | status_label | image_asset_path | button_label | display_order |
|---|---|---|---|---|---|---|---:|
| `agentic-coding` | `Agentic Coding` | `A future pathway for students to design, test, and reflect on AI-assisted coding projects.` | `Coming soon|AI literacy|Project-based learning` | `In development` | `homepage/agentic-coding-card.png` |  | `8` |

Rules:

1. A live card with `button_label` requires a matching curriculum row with `status = published`.
2. An upcoming card must use `status_label` and leave `button_label` empty.
3. A row in `homepage_cards` does not create a curriculum page. Use `curricula`, `units`, and `lessons` for pages.

## Workflow Examples

The following workflows are examples of common edits. Use them as models when changing real website content.

Each workflow ends with the same publishing step: run `Publish Website` in GitHub Actions and check the public website.

## Workflow Example: Change a Curriculum Page Description

Use this workflow when the text at the top of a curriculum page needs to change.

1. Open the `curricula` tab.
2. Find the row for the curriculum. Use the `id` column to identify the row. For example, Act 2 uses `act2`.
3. Edit the `brief_description` cell. Keep this text short because it appears in the page header.
4. Run `Publish Website` in GitHub Actions.
5. Open the public curriculum page and confirm the header description changed.

This workflow changes only the curriculum page. It does not change the homepage card. To change the homepage card, edit `homepage_cards.description`.

## Workflow Example: Change a Homepage Card

Use this workflow when a card on the homepage needs new text, bullets, image, or button text.

1. Open the `homepage_cards` tab.
2. Find the row by `curriculum_id`. For example, Act 2 uses `act2`.
3. Edit `description` for the short paragraph shown on the card.
4. Edit `card_bullet_points` if the bullet list should change. Separate bullets with `|`.
5. Run `Publish Website` in GitHub Actions.
6. Open the homepage and confirm the card changed.

The homepage card and curriculum page are controlled by different tabs. The homepage uses `homepage_cards`; the curriculum page uses `curricula`, `units`, `lessons`, and resource tabs.

## Workflow Example: Replace an Image

Use this workflow when the same content should remain but the image should change.

1. Open the shared Google Drive image folder.
2. Upload the new image into the correct folder. Example folder path: `drive-image-library/homepage/`.
3. Use a clear filename. Example: `data-stories-card.png`.
4. Open the relevant Sheet tab. For a homepage image, use `homepage_cards`. For a unit image, use `units`. For a curriculum cover image, use `curricula`.
5. Update `image_asset_path` with the relative path. Example: `homepage/data-stories-card.png`.
6. Run `Publish Website` in GitHub Actions.
7. Confirm the image changed on the public website.

The GitHub workflow checks that the image path exists. If the path is wrong, publishing fails with an image asset error.

## Workflow Example: Add a New Published Curriculum

Use this workflow when a new curriculum is ready to appear as a live page on the public website.

Do not create a new Sheet tab. Add rows to the existing tabs.

First, add the curriculum page row in `curricula`. Fill the row with these example values:

```text
id: data-stories
title: Data Stories
heading: Data Stories Curriculum
grade_label: Middle School
brief_description: Students investigate data, build visual explanations, and communicate findings through interactive projects.
slug: data-stories.html
status: published
display_order: 6
image_asset_path: curricula/data-stories/cover.png
```

Next, add at least one unit row in `units`. Fill the row with these example values:

```text
curriculum_id: data-stories
unit_id: unit-1
title: Unit 1: Asking Questions With Data
description: Students learn how to ask investigable questions, inspect a dataset, and identify patterns worth explaining.
objectives: Define a data question\nIdentify variables\nDescribe an initial pattern
display_order: 1
image_asset_path: curricula/data-stories/units/unit-1-asking-questions.png
```

Then, add at least one lesson row in `lessons`. Fill the row with these example values:

```text
curriculum_id: data-stories
unit_id: unit-1
lesson_id: lesson-1
title: Lesson 1.1: What Makes a Good Data Question?
description: Students compare sample questions and revise them into questions that can be investigated with data.
objective_bullets: Compare question types|Revise a data question|Explain what makes a question investigable
duration: 45 minutes
display_order: 1
```

After the page has content, add a homepage card in `homepage_cards`. Fill the row with these example values:

```text
curriculum_id: data-stories
title: Data Stories
description: A middle-school pathway for data investigation, visual explanation, and interactive storytelling.
card_bullet_points: Middle School|Data literacy|Interactive storytelling
status_label:
image_asset_path: homepage/data-stories-card.png
button_label: Open Data Stories
display_order: 6
```

Add rows to `lesson_resources` and `teacher_resources` when the curriculum has resource links. Then run `Publish Website`.

After publishing, confirm these results:

1. `data-stories.html` is generated.
2. The homepage shows a `Data Stories` card.
3. The card opens the new page.
4. The navigation dropdown includes `Data Stories`.

## Workflow Example: Add a Unit to an Existing Curriculum

Use this workflow when a curriculum page needs another unit tab.

1. Open the `units` tab.
2. Add a row using an existing `curriculum_id`. For example, Act 2 uses `act2`.
3. Create a new `unit_id`. For example, if the page already has `unit-1` through `unit-4`, use `unit-5`.
4. Fill in `title`, `description`, `objectives`, `display_order`, and `image_asset_path`.
5. Add at least one matching row in `lessons`.
6. Run `Publish Website` in GitHub Actions.
7. Open the curriculum page and confirm the new unit tab appears.

Example `units` row values:

```text
curriculum_id: act2
unit_id: unit-5
title: Unit 5: Extension Project
description: Students extend their Scratch design work with an independent project.
objectives: Plan a project\nBuild and test an interactive Scratch artifact
display_order: 5
image_asset_path: homepage/smile.webp
```

## Workflow Example: Add a Lesson Resource Link

Use this workflow when a lesson needs a new button such as `Slide Deck`, `Lesson Plan`, or `Student Workbook`.

1. Open the `lesson_resources` tab.
2. Add a row using an existing `curriculum_id`, `unit_id`, and `lesson_id`.
3. Fill in `label`, `url`, `resource_type`, and `display_order`.
4. Run `Publish Website` in GitHub Actions.
5. Open the lesson accordion and confirm the new button appears.

Example `lesson_resources` row values:

```text
curriculum_id: act2
unit_id: unit-1
lesson_id: lesson-1
label: Slide Deck
url: https://docs.google.com/presentation/d/example/edit
resource_type: Lesson Resource
display_order: 2
```

## Publishing With GitHub Actions

GitHub Actions publishes the website from the latest Google Sheet and Google Drive image folder. Run it after every content update that should appear on the public website.

Use the steps below each time you want the Sheet and Drive changes to become visible on the public website.

1. Open the GitHub repository page.

The repository page shows the website files and the main GitHub navigation bar. This is the starting place for publishing.

![GitHub repository page for the curriculum website.](../handbook_image/action_1.png)

2. Click `Actions` in the top navigation bar.

The `Actions` tab is where GitHub keeps the publishing workflow.

<img src="../handbook_image/action_2.png" alt="Actions tab in the GitHub navigation bar." class="screenshot-small" />

3. Select `Publish Website` in the left sidebar.

This page lists the previous publishing runs. Use the workflow named `Publish Website`; this is the workflow connected to the public website.

![GitHub Actions page with Publish Website selected.](../handbook_image/action_3.png)

4. Click `Run workflow`.

The button is on the right side of the `Publish Website` workflow page. This starts a new publishing run from the current repository and the latest connected content.

![GitHub Actions Publish Website page showing the Run workflow button.](../handbook_image/action_4.png)

5. Keep the branch set to `main`, then click the green `Run workflow` button.

The branch must be `main`. After clicking the green button, GitHub starts validating the Sheet, building the pages, copying images, and publishing the site.

<img src="../handbook_image/action_5.png" alt="Run workflow menu with branch main and green Run workflow button." class="screenshot-medium" />

6. Wait for the workflow to finish.

A successful run shows a green check. After the green check appears, open the public website and confirm the content or image changed.

Do not use `Re-run all jobs` to publish new edits. Re-running an old job republishes the old commit from that old run and can make the public website look unchanged or outdated.

## Common Validation Errors

If publishing fails, open the failed GitHub Actions run and read the error message. The message usually points to the tab and row that need to be fixed.

| Error | Required fix |
|---|---|
| `status must be 'published' or 'hidden'` | Fix `curricula.status`. |
| `slug must be an .html filename` | Fix `curricula.slug`. Example: `data-stories.html`. |
| `unit_id does not exist` | The row references a unit that does not exist in `units`. |
| `lesson_id does not exist` | The row references a lesson that does not exist in `lessons`. |
| `button_label requires curriculum_id to be a published curriculum` | The homepage card has a button, but the curriculum page is missing or not published. |
| `Could not find image asset` | The `image_asset_path` does not match a file in the shared Drive image folder. Check spelling and extension. |
| Website still looks old after workflow succeeds | Confirm that `Run workflow` was used on branch `main`, not `Re-run all jobs` on an old run. Then hard-refresh the browser with `Cmd + Shift + R`. |
