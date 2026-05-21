from __future__ import annotations

import html
import mimetypes
import os
import re
import sys
from pathlib import Path

from content_loader import HomeCard, Image, Link, Page, Unit, drive_image_resolver, drive_file_id, image_url, load_content, looks_like_url


ROOT = Path(__file__).resolve().parents[1]
GENERATED_IMAGE_DIR = ROOT / "assets" / "generated-images"

FALLBACK_LOGO = "content/drive-image-library/site/logo.png"
PROJECT_URL = "https://www.computingandaiforall.org/"
SITE_TITLE = "Computing and AI for All Curriculum"
HOME_HERO_TITLE = "Computing and AI for All Curriculum"
HEADER_TITLE = "CAIforALL Curriculum"
DIGITAL_LEARNING_LAB_URL = "https://www.digitallearninglab.org/"
CONTACT_EMAIL = "ECforALL@uci.edu"
CREATICODE_EMAIL = "info@creaticode.com"
FEEDBACK_URL = "https://bit.ly/ECforALLfeedback"
ASSET_VERSION = "20260519-footer"
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
    if not image or not image.src:
        return
    if "drive.google.com" in image.src:
        image.src = localize_drive_image(image.src, cache)
        return
    if not looks_like_url(image.src) and not image.src.startswith(("assets/", "content/")):
        local_path = Path("content/drive-image-library") / image.src
        if (ROOT / local_path).exists():
            image.src = local_path.as_posix()


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
    if configured_url:
        return localize_drive_image(image_url(configured_url, configured_path), LOCALIZED_IMAGE_CACHE)
    if (ROOT / FALLBACK_LOGO).exists():
        return FALLBACK_LOGO
    if drive_image_resolver().configured():
        return localize_drive_image(image_url("", configured_path), LOCALIZED_IMAGE_CACHE)
    return FALLBACK_LOGO


def esc(value: str | None) -> str:
    return html.escape(value or "", quote=True)


def display_title(value: str) -> str:
    value = re.sub(r"\bAct\b", "ACT", value or "")
    return re.sub(r"\s+Curriculum\b", "", value).strip()


HERO_PILLS_BY_ID = {
    "act1": ["Scratch", "Grade 4", "Coding Fundamentals"],
    "act2": ["Scratch", "Grade 5", "Animation & Variables"],
    "act3": ["Scratch", "Grades 5–6", "Environment & Data"],
    "act4": ["CreatiCode", "Grades 6–8", "AI Assisted&Agentic Coding"],
    "science_inquiry_studio": ["CreatiCode", "Grades 6–8", "Aligned with NGSS Standards"],
    "scratch": ["Scratch", "Beginner", "Beginner Scratch"],
}


def hero_pills(page: Page) -> list[str]:
    return HERO_PILLS_BY_ID.get(page.id, page.hero_pills)


def is_spanish_resource(label: str) -> bool:
    normalized = (label or "").casefold()
    markers = ("español", "espanol", "spanish", "cuaderno", "vocabulario")
    return any(marker in normalized for marker in markers)


def is_excluded_resource(label: str) -> bool:
    normalized = (label or "").casefold().strip()
    return normalized in {"creaticode platform", "give feedback", "give feedback form", "feedback form"}


def page_head(title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | {esc(SITE_TITLE)}</title>
  <link rel="stylesheet" href="assets/site.css?v={ASSET_VERSION}">
</head>
<body>
"""


def local_href(file: str) -> str:
    return f"{file}?v={ASSET_VERSION}"


def nav(active_file: str, pages: list[Page]) -> str:
    logo = site_logo_url()
    curricula_links = "\n".join(f'<a href="{local_href(page.file)}">{esc(display_title(page.title))}</a>' for page in pages if page.status.lower() != "hidden")
    home_class = ' aria-current="page"' if active_file == "index.html" else ""
    pd_class = ' aria-current="page"' if active_file == "pd.html" else ""
    about_class = ' aria-current="page"' if active_file in {"about.html", "team.html"} else ""
    about_overview_class = ' aria-current="page"' if active_file == "about.html" else ""
    team_class = ' aria-current="page"' if active_file == "team.html" else ""
    help_class = ' aria-current="page"' if active_file == "help.html" else ""
    return f"""
<header class="site-header">
  <div class="nav-inner">
    <a class="brand" href="{local_href("index.html")}"><img alt="" src="{logo}"><span>{esc(HEADER_TITLE)}</span></a>
    <nav class="site-nav" aria-label="Site">
      <a href="{local_href("index.html")}"{home_class}>Home</a>
      <div class="dropdown">
        <button class="dropdown-toggle" type="button">Curricula</button>
        <div class="dropdown-menu">{curricula_links}</div>
      </div>
      <a href="{local_href("pd.html")}"{pd_class}>PD</a>
      <div class="dropdown">
        <button class="dropdown-toggle" type="button"{about_class}>About</button>
        <div class="dropdown-menu"><a href="{PROJECT_URL}" target="_blank" rel="noopener">CAIforAll Project</a>
<a href="{local_href("team.html")}"{team_class}>Team &amp; Partners</a></div>
      </div>
      <a href="{local_href("help.html")}"{help_class}>Contact Us</a>
    </nav>
  </div>
</header>
"""


def footer() -> str:
    return """
<footer class="footer">
  <div class="page-shell">
    <p>Computing and AI for All and its curriculum and other materials are licensed under a Creative Commons Attribution NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0). Under this license, you may use and adapt this work non-commercially as long as you attribute the work to Computing and AI for All and license it under identical terms. You may not use or adapt this work for commercial purposes.</p>
    <p>This curriculum is supported in part by the National Science Foundation through Grants #2317832 and #1923136 and by the United States Department of Education through Grant #U411C190092.</p>
    <p>© 2026, Computing and AI for All</p>
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
    standard = [link for link in selected if not is_spanish_resource(link.label)]
    spanish = [link for link in selected if is_spanish_resource(link.label)]

    def row_html(row_links: list[Link], extra_class: str = "") -> str:
        if not row_links:
            return ""
        return f'<div class="unit-resource-row{extra_class}">' + "".join(
            f'<a class="resource-chip" href="{esc(link.href)}" target="_blank" rel="noopener">{esc(link.label)}</a>'
            for link in row_links
        ) + "</div>"

    return row_html(standard) + row_html(spanish, " spanish-resource-row")


def render_quick_resources(links: list[Link]) -> str:
    selected = [link for link in links if not is_excluded_resource(link.label)]
    if not selected:
        return ""
    standard = [link for link in selected if not is_spanish_resource(link.label)]
    spanish = [link for link in selected if is_spanish_resource(link.label)]

    def row_html(row_links: list[Link], extra_class: str = "") -> str:
        if not row_links:
            return ""
        return f'<div class="quick-resource-row{extra_class}">' + "".join(
            f'<a href="{esc(link.href)}" target="_blank" rel="noopener">{esc(link.label)}</a>'
            for link in row_links
        ) + "</div>"

    return row_html(standard) + row_html(spanish, " quick-resource-row-spanish")


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
    resource_links = render_quick_resources(page.links)
    resource_bar = f"""
    <section class="teacher-resources curriculum-block">
      <h2>Resources</h2>
      <div class="quick-resources" aria-label="Curriculum resources">
        {resource_links}
      </div>
    </section>""" if page.links else ""
    return page_head(page.title) + nav(page.file, all_pages) + f"""
<main>
  <div class="page-shell">
    <section class="curriculum-hero">
      <div class="hero-pills">{"".join(f'<span>{esc(pill)}</span>' for pill in hero_pills(page))}</div>
      <h1>{esc(display_title(page.heading))}</h1>
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
    overview = f'<p class="unit-overview">{esc(unit.description)}</p>' if unit.description else ""
    hidden = "" if index == 1 else " hidden"
    active = " active" if index == 1 else ""
    return f"""
<section class="unit-card unit-panel{active}" id="unit-{index}" role="tabpanel" aria-labelledby="unit-tab-{index}"{hidden}>
  <aside class="unit-media">
    {image}
  </aside>
  <div class="unit-main">
    <h2>{esc(unit.title)}</h2>
    {overview}
    {render_resource_links(unit.links, 4)}
    <div class="lessons">{lessons}</div>
  </div>
</section>
"""


def render_lesson(lesson, open_first: bool) -> str:
    open_attr = " open" if open_first else ""
    duration = f'<span class="duration">{esc(lesson.duration)}</span>' if lesson.duration else ""
    objectives = lesson.objective_bullets or []
    objective_heading = "Learning Objective" if len(objectives) == 1 else "Learning Objectives"
    objective_html = (
        f'<div class="lesson-objectives"><h3>{objective_heading}</h3><ul>'
        + "".join(f"<li>{esc(item)}</li>" for item in objectives[:5])
        + "</ul></div>"
        if objectives
        else ""
    )
    return f"""
<details class="lesson"{open_attr}>
  <summary class="lesson-summary">{esc(lesson.title)}</summary>
  <div class="lesson-body">
    {objective_html}
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
        image = f'<div class="upcoming-art">{esc(card.title)}</div>'
    status_class = ""
    if card.status_label.lower() == "supplementary":
        status_class = " status-chip-supplementary"
    elif card.status_label.lower() == "in development":
        status_class = " status-chip-development"
    status = f'<span class="status-chip{status_class}">{esc(card.status_label)}</span>' if card.status_label else ""
    button = f'<a class="btn outline" href="{esc(card.page.file)}">{esc(card.button_label or "Explore Curriculum")}</a>' if card.page else ""
    upcoming_class = " upcoming" if not card.page else ""
    summary = (
        '<ul class="card-bullets">' + "".join(f"<li>{esc(point)}</li>" for point in card.bullet_points) + "</ul>"
        if card.bullet_points
        else f"<p>{esc(card.description)}</p>"
    )
    return f"""
<article class="pathway-card{upcoming_class}">
  {image}
  <h3>{esc(card.title)}</h3>
  {status}
  {summary}
  {button}
</article>
"""


def render_home(pages: list[Page], cards: list[HomeCard]) -> str:
    card_html = "".join(render_home_card(card) for card in cards)
    return page_head("Home") + nav("index.html", pages) + f"""
<section class="home-hero">
  <div class="page-shell">
    <div>
      <h1>{esc(HOME_HERO_TITLE)}</h1>
      <p>Grounded in NSF-funded research and built for real classrooms,<br>our free K–8 curricula are designed for educators and learners with any background to use with confidence.</p>
      <p class="hero-key-points">Project-Based Learning · Block-Based Coding · AI Literacy · Culturally Relevant · Free</p>
      <div class="btn-row">
        <a class="btn" href="#curricula">Explore the curriculum</a>
        <a class="btn secondary" href="{PROJECT_URL}" target="_blank" rel="noopener">Learn about our research</a>
      </div>
      <p class="hero-credit">Created by the Computing and AI for All team at UC Irvine's <a href="{DIGITAL_LEARNING_LAB_URL}">Digital Learning Lab</a>.</p>
    </div>
  </div>
</section>
<section class="home-section" id="curricula">
  <div class="page-shell">
    <h2>Curricular Pathways</h2>
    <p>Choose the pathway that matches your grade level and learning goals.</p>
    <div class="home-grid">{card_html}</div>
  </div>
</section>
""" + footer()


def render_development_page(page: Page, all_pages: list[Page]) -> str:
    return page_head(page.title) + nav(page.file, all_pages) + f"""
<main>
  <div class="page-shell">
    <section class="curriculum-hero">
      <div class="hero-pills">{"".join(f'<span>{esc(pill)}</span>' for pill in hero_pills(page))}</div>
      <h1>{esc(display_title(page.heading))}</h1>
      <p>{esc(page.summary)}</p>
    </section>
    <section class="development-panel curriculum-block">
      <h2>Pathway Overview</h2>
      <p>Science+AI is being designed as a middle school pathway for science investigation, data-rich inquiry, and AI-assisted coding. The curriculum will support learners in using computing to ask questions, model systems, analyze evidence, and communicate scientific ideas.</p>
      <ul class="card-bullets">
        <li>Grades 6–8</li>
        <li>Aligned with NGSS middle school standards</li>
        <li>AI-assisted coding through science inquiry</li>
      </ul>
      <p>This pathway is currently in development. More units, classroom materials, and teacher resources will be added as they become ready.</p>
      <div class="btn-row">
        <a class="btn outline" href="index.html#curricula">Back to Curricular Pathways</a>
      </div>
    </section>
  </div>
</main>
""" + footer()


def render_about(pages: list[Page]) -> str:
    return page_head("About") + nav("about.html", pages) + f"""
<main class="home-section">
  <div class="page-shell">
    <div class="about-card">
      <h1 style="font-size:48px;line-height:1.05">About Computing and AI for All</h1>
      <p>Computing and AI for All curriculum resources support teachers in bringing computing, AI literacy, computational thinking, collaboration, language development, and project-based learning into classrooms.</p>
      <p>The curriculum collection is connected to the <a href="{PROJECT_URL}">Computing and AI for All</a> project. Visit the main project site to learn more about the team, goals, and broader work behind these materials.</p>
      <div class="btn-row">
        <a class="btn" href="{PROJECT_URL}">Visit Computing and AI for All</a>
        <a class="btn outline" href="index.html">Back to Curriculum Home</a>
      </div>
    </div>
  </div>
</main>
""" + footer()


def render_team(pages: list[Page]) -> str:
    team_body = (ROOT / "team.html").read_text(encoding="utf-8")
    main = re.search(r"(<main.*?</main>)", team_body, re.S)
    return page_head("Team") + nav("team.html", pages) + (main.group(1) if main else "") + footer()


def render_pd(pages: list[Page]) -> str:
    return page_head("PD") + nav("pd.html", pages) + f"""
<section class="pd-hero">
  <div class="page-shell">
    <h1>Professional Development</h1>
  </div>
</section>

<main class="home-section pd-page">
  <div class="page-shell">
    <div class="pd-content">
      <section class="help-section">
        <h2>Self-Paced PD</h2>
        <p>This free, self-paced professional development program will help you learn both the computer science elements and the pedagogical strategies for teaching computational thinking to diverse K-8 students. All those who complete the professional development will be able to implement our curriculum in the classroom.</p>
        <div class="pd-card-grid">
          <article class="pathway-card pd-card pd-card-wide">
            <h3>Unit 0: Introduction to Computing and AI for ALL</h3>
            <p class="pd-card-note">Learn the basics of Scratch block-based coding, the CAI curriculum structure, supporting pedagogy, and how to set up a Scratch classroom.</p>
            <div class="pd-resource-list">
              <a href="https://www.proprofs.com/training/course/?title=copy-of-unit-0-introduction-to-ecforall-and-scratch_68717a6779f53" target="_blank" rel="noopener">Unit 0 Registration</a>
            </div>
          </article>
          <article class="pathway-card pd-card">
            <h3>ACT 1: Scratch Create</h3>
            <div class="pd-resource-list">
              <a href="https://www.proprofstraining.com/app/course/?title=copy-of-act-1-unit-pd_687174ccb0524" target="_blank" rel="noopener">Unit 1: Scratch Basics</a>
              <a href="https://www.proprofstraining.com/app/course/?title=act-unit-2_67feb62ce08b1" target="_blank" rel="noopener">Unit 2: Sequence</a>
              <a href="https://www.proprofstraining.com/app/course/?title=act-unit-3-review_6801676447e51" target="_blank" rel="noopener">Unit 3: Events</a>
              <a href="https://www.proprofstraining.com/app/course/?title=copy-of-act-unit-4-review-in-progress_68717a8528d2d" target="_blank" rel="noopener">Unit 4: Loops</a>
            </div>
          </article>
          <article class="pathway-card pd-card">
            <h3>ACT 2: Scratch Design</h3>
            <div class="pd-resource-list">
              <a href="https://www.proprofstraining.com/app/course/?title=act-2-unit-1-edit-in-progress_6882b341c9df8" target="_blank" rel="noopener">Unit 1: Animation</a>
              <a href="https://www.proprofstraining.com/app/course/?title=act-2-unit-edit-in-progress_6882b37f5b0eb" target="_blank" rel="noopener">Unit 2: Loops with Conditions</a>
              <a href="https://www.proprofstraining.com/app/course/?title=act-2-unit-3-edit-in-progress_6882b45a780c4" target="_blank" rel="noopener">Unit 3: Parallelism and Synchronization</a>
              <a href="https://www.proprofstraining.com/app/course/?title=act-2-unit-4-edit-in-progress_6882b4b7e3265" target="_blank" rel="noopener">Unit 4: Variables</a>
            </div>
          </article>
          <article class="pathway-card pd-card">
            <h3>ACT 3: Scratch Impact</h3>
            <div class="pd-resource-list">
              <a href="https://www.proprofstraining.com/app/course/?title=variables-pd_69b2efd7434c1" target="_blank" rel="noopener">Variables</a>
              <a href="https://www.proprofstraining.com/app/course/?title=variables-pd_69b2ef4d255b6" target="_blank" rel="noopener">If Then-Else Conditional Loops</a>
              <a href="https://www.proprofstraining.com/app/course/?title=act-3-unit-edit-in-progress_6882b6bc54264" target="_blank" rel="noopener">Functions</a>
            </div>
          </article>
        </div>
        <p class="pd-contact-note">PD for additional pathways is in development. For questions, please visit the <a href="help.html">Contact</a> page.</p>
      </section>
      <section class="help-section">
        <h2>For Research Participants</h2>
        <p>Educators and facilitators participating in our research project receive tailored professional development, including training before the course starts and ongoing support throughout implementation. Details vary by cohort.</p>
        <div class="pd-interest">
          <h3>Interested in Participating?</h3>
          <form class="native-interest-form" data-google-form action="https://docs.google.com/forms/d/e/1FAIpQLSeQmgtcbVPH2adjibYN8st1PXsf0b0tlZr2nkN1ueepUsmlsQ/formResponse" method="post" target="interest-form-target">
            <div class="form-grid">
              <label>Your Name <span class="required-star">*</span><input name="entry.1749716936" type="text" autocomplete="name" required></label>
              <label>Your Email <span class="required-star">*</span><input name="entry.398155858" type="email" autocomplete="email" required></label>
              <label>Your School <span class="required-star">*</span><input name="entry.186915610" type="text" required></label>
              <label>Your District <span class="required-star">*</span><input name="entry.846008202" type="text" required></label>
            </div>
            <fieldset data-required-group="entry.1791142999">
              <legend>Project you are interested in <span class="required-star">*</span></legend>
              <label><input name="entry.1791142999" type="checkbox" value="5th Grade: ACT 3"> 5th Grade: ACT 3</label>
              <label><input name="entry.1791142999" type="checkbox" value="6th-8th: Science+AI"> 6th-8th: Science+AI</label>
              <label><input name="entry.1791142999" type="checkbox" value="6th-8th: Coding+AI"> 6th-8th: Coding+AI</label>
            </fieldset>
            <input type="hidden" name="fvv" value="1">
            <input type="hidden" name="pageHistory" value="0">
            <input type="hidden" name="fbzx" value="8190185445833508264">
            <button class="btn primary" type="submit">Submit Interest Form</button>
            <p class="form-status" role="status" aria-live="polite"></p>
          </form>
          <iframe class="hidden-form-target" name="interest-form-target" title="Research participant interest form submission"></iframe>
          <p class="section-note">Prefer Google Forms? <a href="https://docs.google.com/forms/d/e/1FAIpQLSeQmgtcbVPH2adjibYN8st1PXsf0b0tlZr2nkN1ueepUsmlsQ/viewform?usp=header" target="_blank" rel="noopener">Open the original form in a new tab</a>.</p>
        </div>
      </section>
    </div>
  </div>
</main>
""" + footer()


def render_help(pages: list[Page]) -> str:
    return page_head("Contact Us") + nav("help.html", pages) + f"""
<main class="home-section">
  <div class="page-shell">
    <div class="contact-content">
      <h1>Contact Us</h1>
      <p>Please fill out the form below to send an email to CAIforAll Team. Someone will follow up with you ASAP.</p>
      <p>You may also send an email to <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
      <form class="native-interest-form contact-form" data-google-form action="https://docs.google.com/forms/d/e/1FAIpQLSf77OMxLi81HAw0FSxT6OvZInLNTSEi4jchm88xljdFNbmCFg/formResponse" method="post" target="contact-form-target">
        <div class="form-grid">
          <label>Your Name <span class="required-star">*</span><input name="entry.1749716936" type="text" autocomplete="name" required></label>
          <label>Your Email <span class="required-star">*</span><input name="entry.398155858" type="email" autocomplete="email" required></label>
        </div>
        <fieldset data-required-group="entry.1791142999">
          <legend>Related Curricular Pathway <span class="required-star">*</span></legend>
          <label><input name="entry.1791142999" type="checkbox" value="ACT 1"> ACT 1</label>
          <label><input name="entry.1791142999" type="checkbox" value="ACT 2"> ACT 2</label>
          <label><input name="entry.1791142999" type="checkbox" value="ACT 3"> ACT 3</label>
          <label><input name="entry.1791142999" type="checkbox" value="Coding+AI"> Coding+AI</label>
          <label><input name="entry.1791142999" type="checkbox" value="Science+AI"> Science+AI</label>
          <label><input name="entry.1791142999" type="checkbox" value="Scratch Basics"> Scratch Basics</label>
        </fieldset>
        <label>Unit &amp; Lesson <span class="required-star">*</span><input name="entry.1884896097" type="text" placeholder="Example: 2.3, Lesson 2.3, Unit 2 Lesson 2.3" required></label>
        <label>Message <span class="required-star">*</span>
          <textarea name="entry.1233495853" rows="6" required></textarea>
        </label>
        <input type="hidden" name="fvv" value="1">
        <input type="hidden" name="pageHistory" value="0">
        <input type="hidden" name="fbzx" value="-8373193682794724951">
        <button class="btn primary" type="submit">Send Message</button>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
      <iframe class="hidden-form-target" name="contact-form-target" title="Contact form submission"></iframe>
    </div>
  </div>
</main>
""" + footer()


def main() -> None:
    try:
        content = load_content(resolve_images=False)
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
        elif page.status.lower() == "development":
            (ROOT / page.file).write_text(render_development_page(page, content.pages), encoding="utf-8")
    (ROOT / "index.html").write_text(render_home(content.pages, content.homepage_cards), encoding="utf-8")
    (ROOT / "about.html").write_text(render_about(content.pages), encoding="utf-8")
    (ROOT / "team.html").write_text(render_team(content.pages), encoding="utf-8")
    (ROOT / "pd.html").write_text(render_pd(content.pages), encoding="utf-8")
    (ROOT / "help.html").write_text(render_help(content.pages), encoding="utf-8")
    print(f"Built {len(content.pages) + 3} pages from structured content")


if __name__ == "__main__":
    main()
