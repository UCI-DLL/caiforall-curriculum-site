# Content CSV Templates

These CSV files mirror the Google Sheets CMS tabs used by the site generator.

- `curricula.csv`
- `units.csv`
- `lessons.csv`
- `lesson_resources.csv`
- `teacher_resources.csv`
- `homepage_cards.csv`

The live editing workflow should happen in Google Sheets. These CSV files provide a local fallback and a copyable template for the workbook.

See `docs/cms-guide.md` for column definitions and build commands.

For Google Sheets builds, copy `config/cms.env.example` to `config/cms.env` and fill in the real Sheet ID. The private JSON key file should stay outside this website folder.

## Images

The current image upload package lives in `content/drive-image-library/`.

- Upload that folder structure to Google Drive as `CAIforALL Curriculum Images`.
- Share each image as "Anyone with the link can view".
- Paste the local-style file paths into the `image_asset_path` columns in the CMS Sheet.
- Use `content/drive-image-library/image-manifest.csv` as the row-by-row checklist.

Use `image_asset_path` in `curricula`, `units`, and `homepage_cards`. The website generator uses that path to find the matching file inside `GOOGLE_DRIVE_IMAGE_ROOT_ID`.

After adding `image_asset_path` values to the Sheet, run:

```bash
CONTENT_SOURCE=google python3 tools/check_drive_image_paths.py
```
