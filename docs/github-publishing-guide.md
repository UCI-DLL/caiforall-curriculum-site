# GitHub Publishing Guide

This guide sets up a workflow where coworkers edit Google Sheets and Google Drive, then a reviewer presses one button in GitHub to publish the public website.

## What Coworkers Edit

- Google Sheet: curriculum text, lesson rows, resource links, and `image_asset_path` values.
- Google Drive folder: curriculum images using the same folder paths as `image_asset_path`.

Coworkers do not edit HTML, CSS, JavaScript, Python, or GitHub Actions.

## What GitHub Publishes

The GitHub Action publishes only:

- `index.html`
- `about.html`
- `act-1.html`
- `act-2.html`
- `act-3.html`
- `act-4.html`
- `scratch-basics.html`
- `robots.txt`
- `assets/`

It does not publish `config/`, `tools/`, `content/`, `docs/`, or `_original_wix/`.

## One-Time Setup

### 1. Create a GitHub Repository

1. Go to GitHub.
2. Create a new repository.
3. Recommended name: `caiforall-curriculum-site`.
4. Keep it private while testing. You can make it public later if you want.

### 2. Upload This Folder to GitHub

From this folder:

```bash
cd /Users/dinogent/Desktop/Amy/website/www.curriculum.elementarycomputingforall.org
git init
git add .
git commit -m "Set up curriculum website publishing"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/caiforall-curriculum-site.git
git push -u origin main
```

Do not commit `config/cms.env` or the service account JSON file. They are ignored by `.gitignore`.

### 3. Add GitHub Secrets

In the GitHub repository:

1. Go to **Settings**.
2. Go to **Secrets and variables**.
3. Go to **Actions**.
4. Add these **Repository secrets**:

`GOOGLE_SHEET_ID`

The ID from the Google Sheet URL.

`GOOGLE_DRIVE_IMAGE_ROOT_ID`

The ID or full URL for the uploaded `drive-image-library` folder.

`GOOGLE_SERVICE_ACCOUNT_JSON`

The full contents of the service account JSON file. Open the JSON file, copy all of it, and paste it as the secret value.

### 4. Enable GitHub Pages

In the GitHub repository:

1. Go to **Settings**.
2. Go to **Pages**.
3. Under **Build and deployment**, choose **GitHub Actions** as the source.

### 5. Confirm Google Access

The service account email must have viewer access to:

- the Google Sheet
- the Google Drive image folder

The Google Cloud project must have these APIs enabled:

- Google Sheets API
- Google Drive API

## Publishing a Change

1. Coworker edits the Google Sheet or uploads/replaces images in Google Drive.
2. Reviewer opens the GitHub repository.
3. Go to **Actions**.
4. Click **Publish Website**.
5. Click **Run workflow**.
6. Wait for the workflow to finish.

If the workflow succeeds, GitHub shows the public Pages URL in the deployment summary.

If the workflow fails, open the failed step. The error usually says which Sheet row, resource URL, or Drive image path needs fixing.

## Testing From Another Laptop

On another laptop, the reviewer only needs GitHub access.

1. Open the repository in a browser.
2. Go to **Actions**.
3. Run **Publish Website**.
4. Check the result:
   - Green check: website published.
   - Red X: click the failed step and read the error.

No local Python, terminal, or service account file is needed on that laptop.

## Local Preview

For local testing on your machine:

```bash
python3 tools/validate_content.py
python3 tools/check_drive_image_paths.py
python3 tools/build_refined_site.py
```

Then open `index.html` locally or use a simple local server.
