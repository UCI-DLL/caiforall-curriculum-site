# CAIforALL Curriculum CMS Guide

The site is now generated from structured curriculum content instead of hand-edited HTML. Coworkers should edit the Google Sheets workbook; reviewers validate and rebuild the static site.

## Google Sheets Tabs

Create one workbook with these exact tab names and columns.

### Curricula

`id,title,heading,grade_label,brief_description,slug,status,image_asset_path,display_order`

- `id`: stable lowercase id, such as `act2`.
- `slug`: generated page filename, such as `act-2.html`.
- Current curriculum pages use consistent kebab-case filenames:
  `act-1.html`, `act-2.html`, `act-3.html`, `act-4.html`, and `scratch-basics.html`.
- `status`: use `published` for live pages or `hidden` to omit a page from navigation/build output.
- To add a real new curriculum page, use `status` = `published`, use a slug ending in `.html`, and add at least one matching row in `Units`.
- `image_asset_path`: path to the image in the shared Drive image folder, such as `curricula/act2/cover.png`.
- Optional legacy column: `cover_image_drive_url`. If present, a direct URL in this column overrides `image_asset_path`.

### Units

`curriculum_id,unit_id,title,description,objectives,image_asset_path,display_order`

- `curriculum_id`: must match a `Curricula.id`.
- `unit_id`: stable id inside that curriculum, such as `unit-1`.
- `objectives`: plain text; put each objective on a new line.
- `image_asset_path`: path to the image in the shared Drive image folder, such as `curricula/act2/units/unit-1-unit-1-animation.png`.
- Optional legacy column: `image_drive_url`. If present, a direct URL in this column overrides `image_asset_path`.

### Lessons

`curriculum_id,unit_id,lesson_id,title,description,duration,display_order`

- `lesson_id`: stable id inside that unit, such as `lesson-1`.
- `duration`: optional text, such as `50 minutes`.

### Lesson Resources

`curriculum_id,unit_id,lesson_id,label,url,resource_type,display_order`

- Use this for lesson-level resource chips.
- For unit-level resource chips, set `lesson_id` to `__unit__`.
- `url` must start with `http://` or `https://`.

### Teacher Resources

`curriculum_id,label,url,resource_type,display_order`

- These appear in the Teacher resources block below the unit browser.

### Homepage Cards

`curriculum_id,title,description,status_label,image_asset_path,button_label,display_order`

- For live curriculum cards, set `curriculum_id` to a published curriculum id and set `button_label`.
- For upcoming cards, use a future `curriculum_id`, set `status_label` to `In development`, and leave `button_label` blank.
- `image_asset_path`: path to the homepage card image in the shared Drive image folder, such as `homepage/act2-card.png`.
- Optional legacy column: `image_drive_url`. If present, a direct URL in this column overrides `image_asset_path`.

Important: `Curricula` controls curriculum pages and navigation. `Homepage Cards` controls what appears on the homepage grid. Adding a row to `Curricula` alone does not add a homepage card.

## Reviewer Workflow

1. Coworkers edit the Google Sheets workbook.
2. Create a local config file once:

   ```bash
   cp config/cms.env.example config/cms.env
   ```

   Then edit `config/cms.env` and fill in the real `GOOGLE_SHEET_ID`. The `GOOGLE_SERVICE_ACCOUNT_FILE` should point to the downloaded JSON key file. Keep the JSON key outside the website folder.

3. Reviewer previews the content:

   ```bash
   python3 tools/validate_content.py
   ```

4. Reviewer rebuilds the site:

   ```bash
   python3 tools/build_refined_site.py
   ```

5. Reviewer opens the generated pages locally and publishes only after review.

If you need a different config path, set `CMS_CONFIG_FILE`:

```bash
CMS_CONFIG_FILE="/path/to/cms.env" python3 tools/validate_content.py
```

## Local CSV Fallback

The `content/*.csv` files are the same schema as the Google Sheets tabs. They are useful for local preview, backup, and initial template setup.

```bash
CONTENT_SOURCE=csv python3 tools/validate_content.py
CONTENT_SOURCE=csv python3 tools/build_refined_site.py
```

## Google Drive Images

Drive image links are converted into embeddable thumbnail URLs during build. The build can detect malformed Drive links, but reviewers should still preview pages to catch private or deleted images.

Use `image_asset_path` for all curriculum images. The path should match the organized shared Drive folder, such as `curricula/act1/units/unit-1-unit-0-setting-up-scratch-accounts.jpg`.

The older direct URL columns, `cover_image_drive_url` and `image_drive_url`, are still supported as optional override columns for backward compatibility, but they are no longer required.

### Recommended Drive Folder

Create a shared Google Drive folder named `CAIforALL Curriculum Images` and keep the same structure as the local upload package:

```text
CAIforALL Curriculum Images/
  site/
  homepage/
  curricula/
    act1/
      units/
    act2/
      units/
    act3/
      units/
    act4/
      units/
    scratch/
      units/
```

The local package is in `content/drive-image-library/`. Upload those files to Drive, set each image to "Anyone with the link can view", and paste the local file path into each row's `image_asset_path` column.

Use `content/drive-image-library/image-manifest.csv` as the upload checklist. It tells you the local file and the matching spreadsheet tab/row.

Add this to `config/cms.env`:

```bash
GOOGLE_DRIVE_IMAGE_ROOT_ID="paste-your-drive-folder-id-or-folder-url-here"
SITE_LOGO_ASSET_PATH="site/logo.png"
```

Share the Drive folder with the service account email. The folder and image files also need to be viewable by site visitors, usually by setting the folder or files to "Anyone with the link can view"; otherwise the build may find the file but browsers may not display it after publishing.

The Google Cloud project for the service account must have both APIs enabled:

- Google Sheets API
- Google Drive API

The Sheets API reads the workbook. The Drive API resolves `image_asset_path` values and downloads the images into `assets/generated-images/` during the static build, so published pages do not depend on Wix or hotlinked Drive thumbnails.

To rebuild the local upload package from whatever the CMS currently uses:

```bash
python3 tools/download_content_images.py
```

To verify that every `image_asset_path` in the Sheet can be found in the shared Drive folder:

```bash
CONTENT_SOURCE=google python3 tools/check_drive_image_paths.py
```
