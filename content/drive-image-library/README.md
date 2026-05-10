# Drive Image Library

This folder is a local upload package for the Google Drive image folder used by the CMS.

Upload the contents into a shared Google Drive folder named:

`CAIforALL Curriculum Images`

Recommended Drive structure:

- `site/`
  - shared site assets, such as the navigation logo
- `homepage/`
  - homepage card images
- `curricula/{curriculum_id}/`
  - curriculum cover image
- `curricula/{curriculum_id}/units/`
  - unit images for that curriculum page

After uploading, set each image to "Anyone with the link can view", then paste the matching local-style file path into the CMS spreadsheet `image_asset_path` column.

Use `image-manifest.csv` as the checklist. It maps each local image file to:

- the current source URL
- the spreadsheet tab
- the row hint
- the image path column to update
- the suggested Drive folder

The `image_asset_path` column points a row to a file in this folder structure. The site generator uses `image_asset_path` to find the file inside `GOOGLE_DRIVE_IMAGE_ROOT_ID`.
