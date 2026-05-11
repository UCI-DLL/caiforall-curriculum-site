# Content Editor Handbook

This handbook explains the required protocol for updating the Computing and AI for All Curriculum website through Google Sheets and Google Drive.

The editor is responsible for both content edits and publishing. After editing the Sheet or image folder, the editor runs the GitHub workflow and checks the public website.

```text
Edit Google Sheet and/or Google Drive images
Run GitHub Actions > Publish Website > Run workflow
Check the public website
```

## Required Sheet Tabs

The Google Sheet must use these exact tab names. Do not rename them.

| Tab name | Purpose |
|---|---|
| `curricula` | Creates curriculum pages and curriculum navigation entries. |
| `units` | Creates unit tabs/blocks inside curriculum pages. |
| `lessons` | Creates lesson accordions inside units. |
| `lesson_resources` | Creates lesson-level and unit-level resource buttons. |
| `teacher_resources` | Creates curriculum-level resource buttons below the unit browser. |
| `homepage_cards` | Creates cards on the homepage. |

Do not add extra tabs for routine edits. New units, lessons, links, homepage cards, and images must be added as new rows in the existing tabs.

A new tab is allowed only when creating a new curriculum data area outside the current standard structure, and that requires a code update before the website can read it. For normal new curriculum pages, do not add a new tab; add rows to `curricula`, `units`, `lessons`, `lesson_resources`, `teacher_resources`, and `homepage_cards` as needed.

## Image File Paths

Images are stored in the shared Google Drive image folder. The Sheet must use file paths relative to that image folder, not Google Drive share links.

| Image use | Example `image_asset_path` |
|---|---|
| Homepage card image | `homepage/act2-card.png` |
| Curriculum cover image | `curricula/act2/cover.png` |
| Unit image | `curricula/act2/units/unit-1-unit-1-animation.png` |
| Shared temporary image | `homepage/smile.webp` |

A file path must match the folder name, file name, and extension exactly. For example, if the file in Drive is named `act2-card-2026.png`, the Sheet value must be:

```text
homepage/act2-card-2026.png
```

Do not paste a full Google Drive URL into `image_asset_path`.

## Tab Protocol: `curricula`

One row in `curricula` creates one curriculum page.

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

- `status` must be exactly `published` or `hidden`.
- `slug` must end in `.html`.
- A published curriculum page needs at least one matching row in `units`.
- A row in `curricula` does not create a homepage card. Use `homepage_cards` for homepage cards.

## Tab Protocol: `units`

One row in `units` creates one unit tab/block inside a curriculum page.

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

- `curriculum_id` must already exist in `curricula`.
- `unit_id` must be unique within the curriculum.
- Use new rows for new units. Do not create a separate tab for a new unit.

## Tab Protocol: `lessons`

One row in `lessons` creates one lesson accordion inside a unit.

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

- `objective_bullets` uses `|` between bullet items.
- Keep each objective concise and action-focused.
- Use new rows for new lessons. Do not create a separate tab for a new lesson.

## Tab Protocol: `lesson_resources`

One row in `lesson_resources` creates one resource button.

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

- Use `lesson_id = __unit__` for resources shown near the unit description.
- Use a real `lesson_id` for resources shown inside a lesson accordion.
- Resource labels containing `Español`, `Espanol`, or `Spanish` display on a separate resource row.
- `url` must begin with `http://` or `https://`.

## Tab Protocol: `teacher_resources`

One row in `teacher_resources` creates one curriculum-level resource button below the unit browser.

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

- Do not add `CreatiCode Platform`, `Give Feedback`, `Give Feedback Form`, or `Feedback Form` to this tab. These labels are filtered from the website output.

## Tab Protocol: `homepage_cards`

One row in `homepage_cards` creates one homepage card.

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

Rules:

- A live card with `button_label` requires a matching curriculum row with `status = published`.
- An upcoming card must use `status_label` and leave `button_label` empty.
- A row in `homepage_cards` does not create a curriculum page. Use `curricula`, `units`, and `lessons` for pages.

## Workflow: Change a Curriculum Page Description

| Step | Action |
|---:|---|
| 1 | Open the `curricula` tab. |
| 2 | Find the row by `id`. Example: `act2`. |
| 3 | Edit `brief_description`. |
| 4 | Run `Publish Website` in GitHub Actions. |
| 5 | Open the public curriculum page and confirm the hero description changed. |

Note: This does not change the homepage card. To change the homepage card, edit `homepage_cards.description`.

## Workflow: Change a Homepage Card

| Step | Action |
|---:|---|
| 1 | Open the `homepage_cards` tab. |
| 2 | Find the row by `curriculum_id`. Example: `act2`. |
| 3 | Edit `description` or `card_bullet_points`. |
| 4 | Run `Publish Website` in GitHub Actions. |
| 5 | Open the homepage and confirm the card changed. |

## Workflow: Replace an Image

| Step | Action |
|---:|---|
| 1 | Open the shared Google Drive image folder. |
| 2 | Upload the new image into the correct folder. Example folder: `homepage/`. |
| 3 | Use a clear filename. Example: `data-stories-card.png`. |
| 4 | Open the relevant Sheet tab. Example: `homepage_cards`. |
| 5 | Update `image_asset_path`. Example: `homepage/data-stories-card.png`. |
| 6 | Run `Publish Website` in GitHub Actions. |
| 7 | Confirm the image changed on the public website. |

The GitHub workflow checks that the image path exists. If the path is wrong, publishing fails with an image asset error.

## Workflow: Add a New Published Curriculum

Use the existing tabs. Do not create a new tab.

### Step 1: Add a row in `curricula`

| id | title | heading | grade_label | brief_description | slug | status | display_order | image_asset_path |
|---|---|---|---|---|---|---|---:|---|
| `data-stories` | `Data Stories` | `Data Stories Curriculum` | `Middle School` | `Students investigate data, build visual explanations, and communicate findings through interactive projects.` | `data-stories.html` | `published` | `6` | `curricula/data-stories/cover.png` |

### Step 2: Add a row in `units`

| curriculum_id | unit_id | title | description | objectives | display_order | image_asset_path |
|---|---|---|---|---|---:|---|
| `data-stories` | `unit-1` | `Unit 1: Asking Questions With Data` | `Students learn how to ask investigable questions, inspect a dataset, and identify patterns worth explaining.` | `Define a data question\nIdentify variables\nDescribe an initial pattern` | `1` | `curricula/data-stories/units/unit-1-asking-questions.png` |

### Step 3: Add a row in `lessons`

| curriculum_id | unit_id | lesson_id | title | description | objective_bullets | duration | display_order |
|---|---|---|---|---|---|---|---:|
| `data-stories` | `unit-1` | `lesson-1` | `Lesson 1.1: What Makes a Good Data Question?` | `Students compare sample questions and revise them into questions that can be investigated with data.` | `Compare question types|Revise a data question|Explain what makes a question investigable` | `45 minutes` | `1` |

### Step 4: Add a row in `homepage_cards`

| curriculum_id | title | description | card_bullet_points | status_label | image_asset_path | button_label | display_order |
|---|---|---|---|---|---|---|---:|
| `data-stories` | `Data Stories` | `A middle-school pathway for data investigation, visual explanation, and interactive storytelling.` | `Middle School|Data literacy|Interactive storytelling` |  | `homepage/data-stories-card.png` | `Open Data Stories` | `6` |

### Step 5: Add resources as needed

Add rows to `lesson_resources` and `teacher_resources` as needed. These rows are optional, but most published curricula should include teacher-facing resources.

Expected result:

- `data-stories.html` is generated.
- The homepage shows a `Data Stories` card.
- The card opens the new page.
- The navigation dropdown includes `Data Stories`.

## Workflow: Add a Unit to an Existing Curriculum

| Step | Action |
|---:|---|
| 1 | Open the `units` tab. |
| 2 | Add a row with the existing `curriculum_id`. Example: `act2`. |
| 3 | Use a new `unit_id`. Example: `unit-5`. |
| 4 | Add at least one matching row in `lessons`. |
| 5 | Run `Publish Website` in GitHub Actions. |
| 6 | Open the curriculum page and confirm the new unit tab appears. |

Example `units` row:

| curriculum_id | unit_id | title | description | objectives | display_order | image_asset_path |
|---|---|---|---|---|---:|---|
| `act2` | `unit-5` | `Unit 5: Extension Project` | `Students extend their Scratch design work with an independent project.` | `Plan a project\nBuild and test an interactive Scratch artifact` | `5` | `homepage/smile.webp` |

## Workflow: Add a Lesson Resource Link

| Step | Action |
|---:|---|
| 1 | Open the `lesson_resources` tab. |
| 2 | Add a row using an existing `curriculum_id`, `unit_id`, and `lesson_id`. |
| 3 | Run `Publish Website` in GitHub Actions. |
| 4 | Open the lesson accordion and confirm the new button appears. |

Example row:

| curriculum_id | unit_id | lesson_id | label | url | resource_type | display_order |
|---|---|---|---|---|---|---:|
| `act2` | `unit-1` | `lesson-1` | `Slide Deck` | `https://docs.google.com/presentation/d/example/edit` | `Lesson Resource` | `2` |

## Publishing Protocol

| Step | Action |
|---:|---|
| 1 | Open the GitHub repository. |
| 2 | Click `Actions`. |
| 3 | Click `Publish Website` in the left sidebar. |
| 4 | Click `Run workflow`. |
| 5 | Select branch `main`. |
| 6 | Click `Run workflow`. |
| 7 | Wait for the green check. |
| 8 | Open the public website and confirm the update. |

Do not use `Re-run all jobs` to publish new edits. Re-running an old job republishes the old commit from that old run and can make the public website look unchanged or outdated.

## Common Validation Errors

| Error | Required fix |
|---|---|
| `status must be 'published' or 'hidden'` | Fix `curricula.status`. |
| `slug must be an .html filename` | Fix `curricula.slug`. Example: `data-stories.html`. |
| `unit_id does not exist` | The row references a unit that does not exist in `units`. |
| `lesson_id does not exist` | The row references a lesson that does not exist in `lessons`. |
| `button_label requires curriculum_id to be a published curriculum` | The homepage card has a button, but the curriculum page is missing or not published. |
| `Could not find image asset` | The `image_asset_path` does not match a file in the shared Drive image folder. Check spelling and extension. |
| Website still looks old after workflow succeeds | Confirm that `Run workflow` was used on branch `main`, not `Re-run all jobs` on an old run. Then hard-refresh the browser with `Cmd + Shift + R`. |
