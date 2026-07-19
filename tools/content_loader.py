from __future__ import annotations

import base64
import csv
import json
import os
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
DEFAULT_CONFIG_FILE = ROOT / "config" / "cms.env"

SHEET_TABS = {
    "curricula": ["Curriculum Pages", "curricula", "Curricula"],
    "units": ["units", "Units"],
    "lessons": ["lessons", "Lessons"],
    "lesson_resources": ["Lesson Links", "lesson_resources", "Lesson Resources"],
    "teacher_resources": ["Resource Links", "Teacher Resource Links", "teacher_resources", "Teacher Resources"],
    "homepage_cards": ["homepage_cards", "Homepage Cards"],
}

CSV_FILES = {
    "curricula": "curricula.csv",
    "units": "units.csv",
    "lessons": "lessons.csv",
    "lesson_resources": "lesson_resources.csv",
    "teacher_resources": "teacher_resources.csv",
    "homepage_cards": "homepage_cards.csv",
}

CANONICAL_SLUGS = {
    "act1": "act-1.html",
    "act2": "act-2.html",
    "act3": "act-3.html",
    "act4": "act-4.html",
    "scratch": "scratch-basics.html",
}

REQUIRED_COLUMNS = {
    "curricula": [
        "id",
        "title",
        "heading",
        "grade_label",
        "brief_description",
        "slug",
        "status",
        "image_asset_path",
        "display_order",
    ],
    "units": ["curriculum_id", "unit_id", "title", "description", "objectives", "image_asset_path", "display_order"],
    "lessons": ["curriculum_id", "unit_id", "lesson_id", "title", "description", "duration", "display_order"],
    "lesson_resources": ["curriculum_id", "unit_id", "lesson_id", "label", "url", "resource_type", "display_order"],
    "teacher_resources": ["curriculum_id", "label", "url", "resource_type", "display_order"],
    "homepage_cards": [
        "curriculum_id",
        "title",
        "description",
        "bullet_points",
        "status_label",
        "image_asset_path",
        "button_label",
        "display_order",
    ],
}

NONEMPTY_COLUMNS = {
    "curricula": ["id", "title", "heading", "grade_label", "brief_description", "slug", "status", "display_order"],
    "units": ["curriculum_id", "unit_id", "title", "display_order"],
    "lessons": ["curriculum_id", "unit_id", "lesson_id", "title", "display_order"],
    "lesson_resources": ["curriculum_id", "unit_id", "lesson_id", "label", "url", "display_order"],
    "teacher_resources": ["curriculum_id", "label", "url", "display_order"],
    "homepage_cards": ["title", "description", "display_order"],
}

COLUMN_ALIASES = {
    "curricula": {
        "curriculum_id": "id",
        "navigation_title": "title",
        "page_heading": "heading",
        "short_description": "brief_description",
        "page_filename": "slug",
        "publish_status": "status",
        "image_path": "image_asset_path",
        "order": "display_order",
    },
    "units": {
        "unit_title": "title",
        "unit_description": "description",
        "learning_objectives": "objectives",
        "objective_bullets": "objective_bullets",
        "learning_objective_bullets": "objective_bullets",
        "image_path": "image_asset_path",
        "order": "display_order",
    },
    "lessons": {
        "lesson_title": "title",
        "lesson_description": "description",
        "lesson_objective_bullets": "objective_bullets",
        "objective_bullets": "objective_bullets",
        "learning_objective_bullets": "objective_bullets",
        "lesson_duration": "duration",
        "order": "display_order",
    },
    "lesson_resources": {
        "link_label": "label",
        "resource_label": "label",
        "resource_url": "url",
        "link_url": "url",
        "link_type": "resource_type",
        "resource_kind": "resource_type",
        "order": "display_order",
    },
    "teacher_resources": {
        "link_label": "label",
        "resource_label": "label",
        "resource_url": "url",
        "link_url": "url",
        "link_type": "resource_type",
        "resource_kind": "resource_type",
        "order": "display_order",
    },
    "homepage_cards": {
        "card_title": "title",
        "card_description": "description",
        "card_bullet_points": "bullet_points",
        "badge_text": "status_label",
        "status_badge": "status_label",
        "card_button_label": "button_label",
        "image_path": "image_asset_path",
        "order": "display_order",
    },
}


def load_local_config() -> None:
    config_path = Path(os.environ.get("CMS_CONFIG_FILE", DEFAULT_CONFIG_FILE))
    if not config_path.exists():
        return
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_local_config()


@dataclass
class Link:
    label: str
    href: str
    kind: str = "Resource"


@dataclass
class Image:
    src: str
    alt: str = ""


@dataclass
class Lesson:
    id: str
    title: str
    description: str = ""
    objective_bullets: list[str] = field(default_factory=list)
    duration: str = ""
    links: list[Link] = field(default_factory=list)


@dataclass
class Unit:
    id: str
    title: str
    description: str = ""
    objectives: str = ""
    objective_bullets: list[str] = field(default_factory=list)
    image: Image | None = None
    links: list[Link] = field(default_factory=list)
    lessons: list[Lesson] = field(default_factory=list)


@dataclass
class Page:
    id: str
    file: str
    title: str
    heading: str
    grade: str
    quick_title: str
    summary: str = ""
    hero_pills: list[str] = field(default_factory=list)
    status: str = "published"
    cover_image: Image | None = None
    links: list[Link] = field(default_factory=list)
    units: list[Unit] = field(default_factory=list)


@dataclass
class HomeCard:
    curriculum_id: str
    title: str
    description: str
    bullet_points: list[str] = field(default_factory=list)
    status_label: str = ""
    image: Image | None = None
    button_label: str = ""
    page: Page | None = None


@dataclass
class SiteContent:
    pages: list[Page]
    homepage_cards: list[HomeCard]


class ContentError(Exception):
    pass


def clean(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def bullet_points(value: str | None) -> list[str]:
    text = value or ""
    parts = re.split(r"\s*(?:\||;|\n)\s*", text)
    return [clean(part) for part in parts if clean(part)]


def normalize_objective_bullet(value: str) -> str:
    text = clean(value)
    text = re.sub(r"^[\s:：.-]+", "", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+be\s+introduced\s+to\b", "Introduce", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+learn\s+how\s+to\b", "Learn how to", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+learn\s+to\b", "Learn to", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+learn\b", "Learn", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+understand\b", "Understand", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+practice\b", "Practice", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+use\b", "Use", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+create\b", "Create", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+build\b", "Build", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+develop\b", "Develop", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+explore\b", "Explore", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+identify\b", "Identify", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+recognize\b", "Recognize", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+apply\b", "Apply", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+explain\b", "Explain", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\s+work\b", "Work", text)
    text = re.sub(r"\b[Ss]tudents?\s+will\b", "", text)
    text = re.sub(r"^[Bb]e introduced to\b", "Introduce", text)
    text = re.sub(r"^[Ii]ntroduce students to\b", "Introduce", text)
    text = re.sub(r"\b[Ss]tudents?\s+also\s+", "Also ", text)
    text = re.sub(r"\b[Ss]tudents?\s+may\s+also\s+", "Optionally ", text)
    text = re.sub(r"\b[Ss]tudents?\s+work\b", "Work", text)
    text = re.sub(r"\b[Ss]tudents?\s+familiarize\b", "Familiarize", text)
    text = re.sub(r"\b[Ss]tudents?\s+enjoy\b", "Enjoy", text)
    text = re.sub(r"\b[Tt]hey\s+also\s+", "", text)
    text = re.sub(r"\b[Tt]hey\s+will\s+", "", text)
    text = re.sub(r"^[Ss]tudents?\s+play\b", "Play", text)
    text = re.sub(r"^[Ss]tudents?\s+understand\b", "Understand", text)
    text = re.sub(r"^[Ss]tudents?\s+code\b", "Code", text)
    text = re.sub(r"^[Ss]tudents?\s+do\b", "Do", text)
    text = re.sub(r"^[Ss]tudents?\s+plan\b", "Plan", text)
    text = re.sub(r"^[Ss]tudents?\s+view\b", "View", text)
    text = re.sub(r"^[Ss]tudents?\s+self-reflect\b", "Self-reflect", text)
    text = re.sub(r"^[Ss]tudents?\s+define\b", "Define", text)
    text = re.sub(r"^[Ss]tudents?\s+animate\b", "Animate", text)
    text = re.sub(r"^[Ss]tudents?\s+work\b", "Work", text)
    text = re.sub(r"^[Ss]tudents?\s+may\s+also\s+", "Optionally ", text)
    text = re.sub(r"^[Ii]ntroduces students to\b", "Introduce", text)
    text = re.sub(r"^[Ii]ntroduces the\b", "Introduce the", text)
    text = re.sub(r"^[Ww]alks students through\b", "Walk through", text)
    text = re.sub(r"^[Tt]hese lessons teach students that\b", "Teach that", text)
    text = re.sub(r"^[Aa]n existing project by\b", "Modify an existing project by", text)
    text = re.sub(r"^[Aa] Scratch [Pp]roject to\b", "Explore a Scratch project to", text)
    text = re.sub(r"^[Tt]hrough a\b", "Explore through a", text)
    text = re.sub(r"^[Tt]heir\b", "Build their", text)
    text = re.sub(r"\bwill be introduced through\b", "through", text)
    text = re.sub(r"\bwill be introduced\b", "", text)
    text = re.sub(r"\band will play\b", "and play", text)
    text = re.sub(r"\bthey need to understand\b", "needed", text)
    text = re.sub(r"\bfor students to work on\b", "for independent practice", text)
    text = re.sub(r"\bstudents to work on\b", "independent practice", text)
    text = re.sub(r"\bstudents to\b", "", text)
    text = re.sub(r"\bstudents\b", "learners", text)
    text = re.sub(r":\s*([a-z])", lambda match: ": " + match.group(1).upper(), text)
    text = clean(text)
    return text[:1].upper() + text[1:] if text else text


def objective_bullet_points(value: str | None) -> list[str]:
    return [item for item in (normalize_objective_bullet(part) for part in bullet_points(value)) if item]


def canonical_column(table: str, column: str) -> str:
    normalized = clean(column).lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return COLUMN_ALIASES.get(table, {}).get(normalized, normalized)


def normalize_row(table: str, row: dict[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in row.items():
        canonical = canonical_column(table, key)
        value = clean(value)
        if canonical not in normalized or value:
            normalized[canonical] = value
    return normalized


def row_label(table: str, index: int) -> str:
    return f"{table} row {index + 2}"


def order_value(row: dict[str, str], table: str, index: int, errors: list[str]) -> int:
    raw = clean(row.get("display_order"))
    try:
        return int(raw)
    except ValueError:
        errors.append(f"{row_label(table, index)}: display_order must be a number.")
        return 999999


def looks_like_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value))


def drive_file_id(url: str) -> str:
    patterns = [
        r"/file/d/([^/?#]+)",
        r"[?&]id=([^&#]+)",
        r"/open\?id=([^&#]+)",
        r"/uc\?[^#]*id=([^&#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def drive_folder_id(value: str) -> str:
    value = clean(value)
    if not value:
        return ""
    patterns = [
        r"/folders/([^/?#]+)",
        r"[?&]id=([^&#]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)
    return re.split(r"[?#]", value, 1)[0]


def thumbnail_url(file_id: str) -> str:
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1200"


def local_image_asset(asset_path: str) -> str:
    """Return the public local path when a CMS image is bundled in the repo."""
    normalized = "/".join(part for part in clean(asset_path).strip("/").split("/") if part)
    if not normalized:
        return ""
    relative = Path("content") / "drive-image-library" / normalized
    return relative.as_posix() if (ROOT / relative).is_file() else ""


def image_url(value: str, asset_path: str = "", resolve_drive_paths: bool = True) -> str:
    value = clean(value)
    asset_path = clean(asset_path)
    if not value and not asset_path:
        return ""
    if "drive.google.com" in value:
        file_id = drive_file_id(value)
        return thumbnail_url(file_id) if file_id else value
    if value and looks_like_url(value):
        return value
    path = asset_path or value
    if path:
        local_path = local_image_asset(path)
        if local_path:
            return local_path
        if not resolve_drive_paths:
            return path
        return drive_image_resolver().thumbnail_for_path(path)
    return ""


def page_slug(curriculum_id: str, slug: str) -> str:
    return CANONICAL_SLUGS.get(curriculum_id, slug)


def read_csv_tables(content_dir: Path = CONTENT_DIR) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    for key, filename in CSV_FILES.items():
        path = content_dir / filename
        if not path.exists():
            raise ContentError(f"Missing content file: {path}")
        with path.open(newline="", encoding="utf-8") as handle:
            tables[key] = [normalize_row(key, row) for row in csv.DictReader(handle)]
    return tables


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def sign_jwt(unsigned: str, private_key: str) -> str:
    with tempfile.NamedTemporaryFile("w", delete=False) as key_file, tempfile.NamedTemporaryFile("w", delete=False) as data_file:
        key_file.write(private_key)
        key_file.flush()
        data_file.write(unsigned)
        data_file.flush()
        key_path = key_file.name
        data_path = data_file.name
    try:
        signature = subprocess.check_output(["openssl", "dgst", "-sha256", "-sign", key_path, data_path])
        return b64url(signature)
    finally:
        Path(key_path).unlink(missing_ok=True)
        Path(data_path).unlink(missing_ok=True)


def service_account_info() -> dict:
    raw_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    json_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
    if raw_json:
        return json.loads(raw_json)
    if json_path:
        return json.loads(Path(json_path).read_text(encoding="utf-8"))
    raise ContentError("Set GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_JSON to read Google Sheets.")


def google_access_token(scopes: list[str]) -> str:
    import requests

    info = service_account_info()
    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "iss": info["client_email"],
        "scope": " ".join(scopes),
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
    }
    unsigned = f"{b64url(json.dumps(header, separators=(',', ':')).encode())}.{b64url(json.dumps(payload, separators=(',', ':')).encode())}"
    assertion = f"{unsigned}.{sign_jwt(unsigned, info['private_key'])}"
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion},
        timeout=30,
    )
    if response.status_code >= 400:
        raise ContentError(f"Google token request failed: {response.status_code} {response.text}")
    return response.json()["access_token"]


def sheets_access_token() -> str:
    return google_access_token(["https://www.googleapis.com/auth/spreadsheets.readonly"])


def drive_access_token() -> str:
    return google_access_token(["https://www.googleapis.com/auth/drive.readonly"])


class DriveImageResolver:
    def __init__(self) -> None:
        root = os.environ.get("GOOGLE_DRIVE_IMAGE_ROOT_ID") or os.environ.get("GOOGLE_DRIVE_IMAGE_FOLDER_ID", "")
        self.root_id = drive_folder_id(root)
        self.token = ""
        self.children_cache: dict[str, dict[str, dict[str, str]]] = {}
        self.path_cache: dict[str, str] = {}

    def configured(self) -> bool:
        return bool(self.root_id)

    def headers(self) -> dict[str, str]:
        if not self.token:
            self.token = drive_access_token()
        return {"Authorization": f"Bearer {self.token}"}

    def list_children(self, folder_id: str) -> dict[str, dict[str, str]]:
        if folder_id in self.children_cache:
            return self.children_cache[folder_id]
        if not self.configured():
            raise ContentError("Set GOOGLE_DRIVE_IMAGE_ROOT_ID to resolve image_asset_path values.")

        import requests

        children: dict[str, dict[str, str]] = {}
        page_token = ""
        while True:
            params = {
                "q": f"'{folder_id}' in parents and trashed = false",
                "fields": "nextPageToken,files(id,name,mimeType)",
                "pageSize": "1000",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            }
            if page_token:
                params["pageToken"] = page_token
            response = requests.get(
                "https://www.googleapis.com/drive/v3/files",
                headers=self.headers(),
                params=params,
                timeout=30,
            )
            if response.status_code >= 400:
                try:
                    payload = response.json()
                    details = payload.get("error", {})
                    if details.get("status") == "PERMISSION_DENIED" and "disabled" in details.get("message", "").lower():
                        raise ContentError(
                            "Could not read Google Drive image folder because the Google Drive API is disabled for this "
                            "service-account project. Enable Google Drive API in Google Cloud, wait a few minutes, then "
                            "run the build again.\n"
                            f"Google message: {details.get('message')}"
                        )
                except ValueError:
                    pass
                raise ContentError(f"Could not read Google Drive image folder: {response.status_code} {response.text}")
            payload = response.json()
            for file in payload.get("files", []):
                children[file["name"]] = file
            page_token = payload.get("nextPageToken", "")
            if not page_token:
                break
        self.children_cache[folder_id] = children
        return children

    def file_id_for_path(self, asset_path: str) -> str:
        normalized = "/".join(part for part in clean(asset_path).strip("/").split("/") if part)
        if not normalized:
            raise ContentError("Image asset path is empty.")
        if normalized in self.path_cache:
            return self.path_cache[normalized]

        current_id = self.root_id
        parts = normalized.split("/")
        for index, part in enumerate(parts):
            children = self.list_children(current_id)
            file = children.get(part)
            if not file:
                raise ContentError(f"Could not find image asset '{normalized}' in Google Drive folder.")
            if index < len(parts) - 1 and file.get("mimeType") != "application/vnd.google-apps.folder":
                raise ContentError(f"Image asset path '{normalized}' expected '{part}' to be a folder.")
            current_id = file["id"]

        self.path_cache[normalized] = current_id
        return current_id

    def thumbnail_for_path(self, asset_path: str) -> str:
        return thumbnail_url(self.file_id_for_path(asset_path))


_DRIVE_IMAGE_RESOLVER: DriveImageResolver | None = None


def drive_image_resolver() -> DriveImageResolver:
    global _DRIVE_IMAGE_RESOLVER
    if _DRIVE_IMAGE_RESOLVER is None:
        _DRIVE_IMAGE_RESOLVER = DriveImageResolver()
    return _DRIVE_IMAGE_RESOLVER


def sheet_rows(table: str, values: list[list[str]]) -> list[dict[str, str]]:
    if not values:
        return []
    headers = [canonical_column(table, value) for value in values[0]]
    rows: list[dict[str, str]] = []
    for raw in values[1:]:
        padded = raw + [""] * (len(headers) - len(raw))
        rows.append(normalize_row(table, {header: value for header, value in zip(headers, padded)}))
    return rows


def read_google_tables(sheet_id: str | None = None) -> dict[str, list[dict[str, str]]]:
    sheet_id = sheet_id or os.environ.get("GOOGLE_SHEET_ID", "").strip()
    if not sheet_id:
        raise ContentError("Set GOOGLE_SHEET_ID to read Google Sheets.")
    import requests

    token = sheets_access_token()
    tables: dict[str, list[dict[str, str]]] = {}
    for key, tab_names in SHEET_TABS.items():
        last_error = ""
        for tab_name in tab_names:
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{quote(tab_name)}"
            response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
            if response.status_code < 400:
                tables[key] = sheet_rows(key, response.json().get("values", []))
                break
            last_error = f"{response.status_code} {response.text}"
        else:
            names = ", ".join(f"'{name}'" for name in tab_names)
            raise ContentError(f"Could not read Google Sheet tab {names}: {last_error}")
    return tables


def validate_tables(tables: dict[str, list[dict[str, str]]], resolve_images: bool = True) -> list[str]:
    errors: list[str] = []
    for table, columns in REQUIRED_COLUMNS.items():
        if table not in tables:
            errors.append(f"Missing table: {table}")
            continue
        found = set(tables[table][0].keys()) if tables[table] else set(columns)
        for column in columns:
            if column not in found:
                errors.append(f"{table}: missing required column '{column}'.")
        for index, row in enumerate(tables[table]):
            for column in NONEMPTY_COLUMNS[table]:
                if not clean(row.get(column)):
                    errors.append(f"{row_label(table, index)}: '{column}' is required.")
            order_value(row, table, index, errors)

    for index, row in enumerate(tables.get("curricula", [])):
        status = clean(row.get("status")).lower()
        slug = clean(row.get("slug"))
        if status not in {"published", "hidden", "development"}:
            errors.append(f"{row_label('curricula', index)}: status must be 'published', 'development', or 'hidden'.")
        if slug and not slug.endswith(".html"):
            errors.append(f"{row_label('curricula', index)}: slug must be an .html filename, such as 'test-remote.html'.")

    curricula = {row.get("id", "") for row in tables.get("curricula", [])}
    published_curricula = {
        row.get("id", "")
        for row in tables.get("curricula", [])
        if clean(row.get("status")).lower() == "published"
    }
    units = {(row.get("curriculum_id", ""), row.get("unit_id", "")) for row in tables.get("units", [])}
    lesson_keys = {(row.get("curriculum_id", ""), row.get("unit_id", ""), row.get("lesson_id", "")) for row in tables.get("lessons", [])}

    for table in ["units", "teacher_resources"]:
        for index, row in enumerate(tables.get(table, [])):
            if row.get("curriculum_id") not in curricula:
                errors.append(f"{row_label(table, index)}: curriculum_id '{row.get('curriculum_id')}' does not exist.")

    for table in ["lessons", "lesson_resources"]:
        for index, row in enumerate(tables.get(table, [])):
            unit_key = (row.get("curriculum_id", ""), row.get("unit_id", ""))
            if row.get("curriculum_id") not in curricula:
                errors.append(f"{row_label(table, index)}: curriculum_id '{row.get('curriculum_id')}' does not exist.")
            elif unit_key not in units:
                errors.append(f"{row_label(table, index)}: unit_id '{row.get('unit_id')}' does not exist for curriculum '{row.get('curriculum_id')}'.")

    for index, row in enumerate(tables.get("lesson_resources", [])):
        if row.get("lesson_id") == "__unit__":
            continue
        lesson_key = (row.get("curriculum_id", ""), row.get("unit_id", ""), row.get("lesson_id", ""))
        if lesson_key not in lesson_keys:
            errors.append(f"{row_label('lesson_resources', index)}: lesson_id '{row.get('lesson_id')}' does not exist.")

    for table in ["lesson_resources", "teacher_resources"]:
        for index, row in enumerate(tables.get(table, [])):
            if row.get("url") and not looks_like_url(row["url"]):
                errors.append(f"{row_label(table, index)}: url must start with http:// or https://.")

    for index, row in enumerate(tables.get("homepage_cards", [])):
        curriculum_id = clean(row.get("curriculum_id"))
        button_label = clean(row.get("button_label"))
        status_label = clean(row.get("status_label"))
        bullets = bullet_points(row.get("bullet_points"))
        if len(bullets) > 4:
            errors.append(f"{row_label('homepage_cards', index)}: bullet_points should contain 4 or fewer items.")
        if button_label and curriculum_id not in published_curricula:
            errors.append(
                f"{row_label('homepage_cards', index)}: button_label requires curriculum_id '{curriculum_id}' to be a published curriculum."
            )
        if curriculum_id and curriculum_id not in curricula and not status_label:
            errors.append(
                f"{row_label('homepage_cards', index)}: unknown curriculum_id '{curriculum_id}' needs a status_label such as 'In development'."
            )

    for table in ["curricula", "units", "homepage_cards"]:
        column = "cover_image_drive_url" if table == "curricula" else "image_drive_url"
        for index, row in enumerate(tables.get(table, [])):
            value = row.get(column, "")
            asset_path = row.get("image_asset_path", "")
            if "drive.google.com" in value and not drive_file_id(value):
                errors.append(f"{row_label(table, index)}: Google Drive image link is missing a file id.")
            elif value and not looks_like_url(value) and not drive_image_resolver().configured():
                errors.append(
                    f"{row_label(table, index)}: image link must start with http:// or https:// unless GOOGLE_DRIVE_IMAGE_ROOT_ID is set."
                )
            elif resolve_images and asset_path and not local_image_asset(asset_path) and not drive_image_resolver().configured() and not value:
                errors.append(f"{row_label(table, index)}: image_asset_path requires GOOGLE_DRIVE_IMAGE_ROOT_ID.")

    return errors


def sorted_rows(rows: Iterable[dict[str, str]], table: str, errors: list[str]) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: order_value(row, table, 0, errors))


def build_content(tables: dict[str, list[dict[str, str]]], resolve_images: bool = True) -> SiteContent:
    errors = validate_tables(tables, resolve_images=resolve_images)
    if errors:
        raise ContentError("Content validation failed:\n" + "\n".join(f"- {error}" for error in errors))

    pages_by_id: dict[str, Page] = {}
    pages: list[Page] = []
    for row in sorted_rows(tables["curricula"], "curricula", []):
        page = Page(
            id=row["id"],
            file=page_slug(row["id"], row["slug"]),
            title=row["title"],
            heading=row["heading"],
            grade=row["grade_label"],
            quick_title=row["title"].split(":", 1)[0],
            summary=row["brief_description"],
            status=row["status"],
            cover_image=Image(
                image_url(row.get("cover_image_drive_url", ""), row.get("image_asset_path", ""), resolve_images),
                row["title"],
            )
            if row.get("cover_image_drive_url") or row.get("image_asset_path")
            else None,
        )
        pages_by_id[page.id] = page
        if page.status.lower() != "hidden":
            pages.append(page)

    units_by_key: dict[tuple[str, str], Unit] = {}
    for row in sorted_rows(tables["units"], "units", []):
        image = (
            Image(image_url(row.get("image_drive_url", ""), row.get("image_asset_path", ""), resolve_images), row["title"])
            if row.get("image_drive_url") or row.get("image_asset_path")
            else None
        )
        unit = Unit(
            row["unit_id"],
            row["title"],
            row.get("description", ""),
            row.get("objectives", ""),
            bullet_points(row.get("objective_bullets")),
            image,
        )
        units_by_key[(row["curriculum_id"], row["unit_id"])] = unit
        pages_by_id[row["curriculum_id"]].units.append(unit)

    lessons_by_key: dict[tuple[str, str, str], Lesson] = {}
    for row in sorted_rows(tables["lessons"], "lessons", []):
        lesson = Lesson(
            row["lesson_id"],
            row["title"],
            row.get("description", ""),
            objective_bullet_points(row.get("objective_bullets")),
            row.get("duration", ""),
        )
        lessons_by_key[(row["curriculum_id"], row["unit_id"], row["lesson_id"])] = lesson
        units_by_key[(row["curriculum_id"], row["unit_id"])].lessons.append(lesson)

    for row in sorted_rows(tables["lesson_resources"], "lesson_resources", []):
        link = Link(row["label"], row["url"], row.get("resource_type", "Resource"))
        if row["lesson_id"] == "__unit__":
            unit = units_by_key[(row["curriculum_id"], row["unit_id"])]
            if clean(row["label"]).lower() == "teacher manual":
                unit.lessons.insert(0, Lesson("__teacher_manual__", "Teacher Manual", "", [], "", [link]))
            else:
                unit.links.append(link)
        else:
            lessons_by_key[(row["curriculum_id"], row["unit_id"], row["lesson_id"])].links.append(link)

    for row in sorted_rows(tables["teacher_resources"], "teacher_resources", []):
        pages_by_id[row["curriculum_id"]].links.append(Link(row["label"], row["url"], row.get("resource_type", "Resource")))

    cards: list[HomeCard] = []
    for row in sorted_rows(tables["homepage_cards"], "homepage_cards", []):
        page = pages_by_id.get(row.get("curriculum_id", ""))
        image = (
            Image(image_url(row.get("image_drive_url", ""), row.get("image_asset_path", ""), resolve_images), row["title"])
            if row.get("image_drive_url") or row.get("image_asset_path")
            else None
        )
        if not image and page:
            image = page.cover_image
        cards.append(
            HomeCard(
                curriculum_id=row.get("curriculum_id", ""),
                title=row["title"],
                description=row["description"],
                bullet_points=bullet_points(row.get("bullet_points")),
                status_label=row.get("status_label", ""),
                image=image,
                button_label=row.get("button_label", ""),
                page=page,
            )
        )
        if page and row.get("bullet_points"):
            page.hero_pills = bullet_points(row.get("bullet_points"))

    return SiteContent(pages, cards)


def load_content(source: str | None = None, resolve_images: bool = True) -> SiteContent:
    source = source or os.environ.get("CONTENT_SOURCE", "csv")
    if source == "google":
        tables = read_google_tables()
    elif source == "csv":
        tables = read_csv_tables()
    else:
        raise ContentError("CONTENT_SOURCE must be 'csv' or 'google'.")
    return build_content(tables, resolve_images=resolve_images)
