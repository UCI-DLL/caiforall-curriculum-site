from __future__ import annotations

import html
import mimetypes
import os
import re
import sys
from pathlib import Path

from content_loader import HomeCard, Image, Link, Page, Unit, drive_image_resolver, drive_file_id, image_url, load_content


ROOT = Path(__file__).resolve().parents[1]
GENERATED_IMAGE_DIR = ROOT / "assets" / "generated-images"

FALLBACK_LOGO = "content/drive-image-library/site/logo.png"
PROJECT_URL = "https://www.computingandaiforall.org/"
LOCALIZED_IMAGE_CACHE: dict[str, str] = {}


def extension_from_content_type(content_type: str) -> str:
    content_type = content_type.split(";", 1)[0].strip().lower()
    if content_type == "image/jpeg":
        return ".jpg"
    guessed = mimetypes.guess_extension(content_type)
    return guessed if guessed in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"} else ".jpg"


def localize_drive_image(src: str, cache: dict[str, str]) -> str:
    file_id = drive_file_id(src)
    if not file_id:
        return src
    if file_id in cache:
        return cache[file_id]

    import requests

    response = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}",
        headers=drive_image_resolver().headers(),
        params={"alt": "media", "supportsAllDrives": "true"},
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Could not download Drive image {file_id}: {response.status_code} {response.text}")

    ext = extension_from_content_type(response.headers.get("content-type", ""))
    GENERATED_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GENERATED_IMAGE_DIR / f"{file_id}{ext}"
    output_path.write_bytes(response.content)
    relative = output_path.relative_to(ROOT).as_posix()
    cache[file_id] = relative
    return relative


def localize_image(image: Image | None, cache: dict[str, str]) -> None:
    if image and image.src and "drive.google.com" in image.src:
        image.src = localize_drive_image(image.src, cache)


def localize_site_images(pages: list[Page], cards: list[HomeCard]) -> None:
    cache: dict[str, str] = {}
    for page in pages:
        localize_image(page.cover_image, cache)
        for unit in page.units:
            localize_image(unit.image, cache)
    for card in cards:
        localize_image(card.image, cache)


def site_logo_url() -> str:
    configured_url = os.environ.get("SITE_LOGO_IMAGE_URL", "")
    configured_path = os.environ.get("SITE_LOGO_ASSET_PATH", "site/logo.png")
    if configured_url or drive_image_resolver().configured():
        return localize_drive_image(image_url(configured_url, configured_path), LOCALIZED_IMAGE_CACHE)
    return FALLBACK_LOGO


def esc(value: str | None) -> str:
    return html.escape(value or "", quote=True)


def page_head(title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | CAIforALL Curriculum</title>
  <link rel="stylesheet" href="assets/site.css">
</head>
<body>
"""


def nav(active_file: str, pages: list[Page]) -> str:
    logo = site_logo_url()
    curricula_links = "\n".join(f'<a href="{page.file}">{esc(page.title)}</a>' for page in pages if page.status.lower() == "published")
    home_class = ' aria-current="page"' if active_file == "index.html" else ""
    about_class = ' aria-current="page"' if active_file == "about.html" else ""
    return f"""
<header class="site-header">
  <div class="nav-inner">
    <a class="brand" href="index.html"><img alt="" src="{logo}"><span>CAIforALL Curriculum</span></a>
    <nav class="site-nav" aria-label="Site">
      <a href="index.html"{home_class}>Home</a>
      <div class="dropdown">
        <button class="dropdown-toggle" type="button">Curricula</button>
        <div class="dropdown-menu">{curricula_links}</div>
      </div>
      <a href="about.html"{about_class}>About CAIforALL</a>
      <div class="dropdown">
        <button class="dropdown-toggle" type="button">More</button>
        <div class="dropdown-menu">
          <a href="{PROJECT_URL}">Computing & AI for All</a>
          <a href="https://www.elementarycomputingforall.org/">Elementary Computing for All</a>
          <a href="https://scratch.mit.edu/">Scratch</a>
          <a href="https://bit.ly/ECforALLfeedback">Feedback Form</a>
        </div>
      </div>
    </nav>
  </div>
</header>
"""


def footer() -> str:
    return f"""
<footer class="footer">
  <div class="page-shell">
    <p>CAIforALL Curriculum. Created in affiliation with <a href="{PROJECT_URL}">Computing & AI for All</a>.</p>
  </div>
</footer>
<script src="assets/site.js"></script>
</body>
</html>
"""


def render_resource_links(links: list[Link], limit: int | None = None) -> str:
    selected = links[:limit] if limit else links
    if not selected:
        return ""
    return '<div class="unit-resource-row">' + "".join(
        f'<a class="resource-chip {"primary" if i < 2 else ""}" href="{esc(link.href)}" target="_blank" rel="noopener">{esc(link.label)}</a>'
        for i, link in enumerate(selected)
    ) + "</div>"


def render_objectives(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    lines = [re.sub(r"^\s*\d+[.)]\s*", "", line).strip() for line in re.split(r"\n+|(?:\s*;\s*)", text) if line.strip()]
    if len(lines) > 1:
        return "<ol>" + "".join(f"<li>{esc(line)}</li>" for line in lines) + "</ol>"
    return f"<p>{esc(text)}</p>"


def short_unit_title(title: str) -> str:
    match = re.match(r"^(Unit\s*\d+)", title, re.I)
    return re.sub(r"\s+", " ", match.group(1)) if match else title


def render_curriculum(page: Page, all_pages: list[Page]) -> str:
    tabs = "".join(
        f'<button class="unit-tab{" active" if i == 0 else ""}" id="unit-tab-{i+1}" type="button" data-unit-target="unit-{i+1}" role="tab" aria-controls="unit-{i+1}" aria-selected="{"true" if i == 0 else "false"}">{esc(short_unit_title(unit.title))}</button>'
        for i, unit in enumerate(page.units)
    )
    unit_html = "".join(render_unit(unit, i + 1) for i, unit in enumerate(page.units))
    resource_links = "".join(
        f'<a href="{esc(link.href)}" target="_blank" rel="noopener">{esc(link.label)}</a>'
        for link in page.links
    )
    resource_bar = f"""
    <section class="teacher-resources curriculum-block">
      <h2>Teacher resources</h2>
      <div class="quick-resources" aria-label="Curriculum resources">
        {resource_links}
      </div>
    </section>""" if page.links else ""
    return page_head(page.title) + nav(page.file, all_pages) + f"""
<main>
  <div class="page-shell">
    <section class="curriculum-hero">
      <div class="hero-kicker">{esc(page.grade)} curriculum</div>
      <h1>{esc(page.heading)}</h1>
      <p>{esc(page.summary)}</p>
    </section>
    <section class="unit-browser curriculum-block" data-unit-browser>
      <div class="unit-tabs" role="tablist" aria-label="Curriculum units">
        {tabs}
      </div>
      <div class="unit-panels">
        {unit_html}
      </div>
    </section>
    {resource_bar}
  </div>
</main>
""" + footer()


def render_unit(unit: Unit, index: int) -> str:
    image = f'<img src="{esc(unit.image.src)}" alt="{esc(unit.image.alt or unit.title)}">' if unit.image and unit.image.src else '<div class="image-placeholder">Curriculum image</div>'
    lessons = "".join(render_lesson(lesson, i == 0) for i, lesson in enumerate(unit.lessons))
    hidden = "" if index == 1 else " hidden"
    active = " active" if index == 1 else ""
    return f"""
<section class="unit-card unit-panel{active}" id="unit-{index}" role="tabpanel" aria-labelledby="unit-tab-{index}"{hidden}>
  <aside class="unit-media">
    {image}
    <div class="objectives">
      <h3>Learning Objectives</h3>
      {render_objectives(unit.objectives)}
    </div>
  </aside>
  <div class="unit-main">
    <h2>{esc(unit.title)}</h2>
    {render_resource_links(unit.links, 4)}
    <p class="unit-overview">{esc(unit.description)}</p>
    <div class="lessons">{lessons}</div>
  </div>
</section>
"""


def render_lesson(lesson, open_first: bool) -> str:
    open_attr = " open" if open_first else ""
    duration = f'<span class="duration">{esc(lesson.duration)}</span>' if lesson.duration else ""
    return f"""
<details class="lesson"{open_attr}>
  <summary class="lesson-summary">{esc(lesson.title)}</summary>
  <div class="lesson-body">
    <p>{esc(lesson.description)}</p>
    {duration}
    {render_resource_links(lesson.links, 6)}
  </div>
</details>
"""


def initials(title: str) -> str:
    bits = re.findall(r"[A-Za-z0-9]+", title)
    return "".join(bit[0].upper() for bit in bits[:3]) or "NEW"


def render_home_card(card: HomeCard) -> str:
    image = ""
    if card.image and card.image.src:
        image = f'<img src="{esc(card.image.src)}" alt="{esc(card.image.alt or card.title)}">'
    else:
        image = f'<div class="upcoming-art">{esc(initials(card.title))}</div>'
    status = f'<span class="status-chip">{esc(card.status_label)}</span>' if card.status_label else ""
    button = f'<a class="btn outline" href="{esc(card.page.file)}">{esc(card.button_label or "Open Curriculum")}</a>' if card.page else ""
    upcoming_class = " upcoming" if not card.page else ""
    return f"""
<article class="pathway-card{upcoming_class}">
  {image}
  {status}
  <h3>{esc(card.title)}</h3>
  <p>{esc(card.description)}</p>
  {button}
</article>
"""


def render_home(pages: list[Page], cards: list[HomeCard]) -> str:
    card_html = "".join(render_home_card(card) for card in cards)
    hero_image = next((card.image for card in cards if card.image and card.page), None)
    hero_media = f'<img src="{esc(hero_image.src)}" alt="{esc(hero_image.alt)}">' if hero_image else f'<img src="{site_logo_url()}" alt="">'
    return page_head("Home") + nav("index.html", pages) + f"""
<section class="home-hero">
  <div class="page-shell">
    <div>
      <div class="hero-kicker">Curriculum hub</div>
      <h1>CAIforALL Curriculum</h1>
      <p>Organized curriculum pathways for Scratch coding, computational thinking, environmental impact projects, and AI literacy.</p>
      <p>Created by our curriculum team in affiliation with the <a href="{PROJECT_URL}">Computing & AI for All</a> project.</p>
      <div class="btn-row">
        <a class="btn" href="#curricula">Browse Curricula</a>
        <a class="btn secondary" href="{PROJECT_URL}">Visit Main Project</a>
      </div>
    </div>
    <div class="hero-panel">{hero_media}</div>
  </div>
</section>
<section class="home-section" id="curricula">
  <div class="page-shell">
    <h2>Curriculum Pathways</h2>
    <p>Choose the pathway that matches your grade band and teaching goals. Current pathways are ready to use; new pathways are being prepared.</p>
    <div class="home-grid">{card_html}</div>
  </div>
</section>
""" + footer()


def render_about(pages: list[Page]) -> str:
    return page_head("About CAIforALL") + nav("about.html", pages) + f"""
<main class="home-section">
  <div class="page-shell">
    <div class="about-card">
      <h1 style="font-size:48px;line-height:1.05">About CAIforALL</h1>
      <p>CAIforALL curriculum resources support teachers in bringing computing, AI literacy, computational thinking, collaboration, language development, and project-based learning into classrooms.</p>
      <p>The curriculum collection is connected to the <a href="{PROJECT_URL}">Computing & AI for All</a> project. Visit the main project site to learn more about the team, goals, and broader work behind these materials.</p>
      <div class="btn-row">
        <a class="btn" href="{PROJECT_URL}">Visit Computing & AI for All</a>
        <a class="btn outline" href="index.html">Back to Curriculum Home</a>
      </div>
    </div>
  </div>
</main>
""" + footer()


def main() -> None:
    try:
        content = load_content()
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)

    try:
        localize_site_images(content.pages, content.homepage_cards)
    except Exception as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)

    for page in content.pages:
        if page.status.lower() == "published":
            (ROOT / page.file).write_text(render_curriculum(page, content.pages), encoding="utf-8")
    (ROOT / "index.html").write_text(render_home(content.pages, content.homepage_cards), encoding="utf-8")
    (ROOT / "about.html").write_text(render_about(content.pages), encoding="utf-8")
    print(f"Built {len(content.pages) + 2} pages from structured content")


if __name__ == "__main__":
    main()
