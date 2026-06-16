import os
import re
import subprocess
from datetime import datetime, timezone
from html import unescape
from importlib.metadata import PackageNotFoundError, version as package_version


from mkdocs.utils import log


ALLOWED_PATTERNS = [
    r"^index\.html$",
    r"^(features|release_notes)/index\.html$",
    r"^learn/.*/index\.html$",
    r"^reference/.*/index\.html$",
    r"^examples/.*/index\.html$",
]

EXCLUDED = {
    "404.html",
    "sitemap.xml",
    "objects.inv",
}

SECTION_LABELS = {
    "learn": "Learn",
    "reference": "Reference",
    "examples": "Examples",
}

SECTION_ORDER = {
    "root": 0,
    "learn": 1,
    "reference": 2,
    "examples": 3,
    "other": 4,
}

BLOCK_TAGS = ("p", "div", "section", "article", "blockquote")
LIST_TAGS = ("ul", "ol")


def should_include_page(path: str) -> bool:
    """Return True when the rendered file should be included in llms outputs."""
    normalized = path.replace("\\", "/").lstrip("/")

    if normalized in EXCLUDED:
        return False

    if not normalized.endswith(".html"):
        return False

    if normalized.startswith("ru/") or "/ru/" in normalized:
        return False

    return any(re.match(pattern, normalized) for pattern in ALLOWED_PATTERNS)


def extract_main_content(html: str) -> str:
    """Extract the main Material content area from rendered HTML."""
    patterns = [
        r'<article class="md-content__inner md-typeset">(.*?)</article>',
        r"<article[^>]*class=\"[^\"]*md-content__inner[^\"]*md-typeset[^\"]*\"[^>]*>(.*?)</article>",
        r"<main[^>]*>(.*?)</main>",
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)

    return html


def strip_tags(value: str) -> str:
    """Remove HTML tags and normalize whitespace in a short fragment."""
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph-like spacing."""
    text = text.replace("\r", "")
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def convert_table_to_markdown(table_html: str) -> str:
    """Convert a basic HTML table to Markdown."""
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.DOTALL | re.IGNORECASE)
    parsed_rows = []

    for row in rows:
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.DOTALL | re.IGNORECASE)
        cleaned = [normalize_text(html_to_markdown(cell)) for cell in cells]
        if cleaned:
            parsed_rows.append(cleaned)

    if not parsed_rows:
        return ""

    column_count = max(len(row) for row in parsed_rows)
    padded_rows = [row + [""] * (column_count - len(row)) for row in parsed_rows]

    header = padded_rows[0]
    separator = ["---"] * column_count
    body = padded_rows[1:]

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]

    for row in body:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def convert_details_to_markdown(details_html: str) -> str:
    """Convert details/summary blocks into visible Markdown sections."""
    summary_match = re.search(
        r"<summary[^>]*>(.*?)</summary>",
        details_html,
        re.DOTALL | re.IGNORECASE,
    )
    summary = strip_tags(summary_match.group(1)) if summary_match else "Details"

    content = re.sub(
        r"<summary[^>]*>.*?</summary>",
        "",
        details_html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Avoid recursive processing when details blocks are nested.
    content = re.sub(
        r"<summary[^>]*>(.*?)</summary>",
        lambda match: f"<h4>{strip_tags(match.group(1))}</h4>",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    content = re.sub(r"</?details[^>]*>", "", content, flags=re.IGNORECASE)

    content_md = normalize_text(html_to_markdown(content))

    if content_md:
        return f"\n\n### {summary}\n\n{content_md}\n\n"

    return f"\n\n### {summary}\n\n"


def html_to_markdown(html: str) -> str:
    """Convert rendered HTML into readable Markdown for llms outputs."""
    if not html:
        return ""

    text = html

    text = re.sub(
        r"<script\b[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(
        r"<style\b[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(
        r"<a[^>]*class=\"[^\"]*headerlink[^\"]*\"[^>]*>.*?</a>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(
        r"<span[^>]*class=\"[^\"]*gp[^\"]*\"[^>]*>.*?</span>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(r"</?span[^>]*>", "", text, flags=re.IGNORECASE)

    text = re.sub(
        r"<details\b[^>]*>.*?</details>",
        lambda match: convert_details_to_markdown(match.group(0)),
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<table\b[^>]*>.*?</table>",
        lambda match: "\n\n" + convert_table_to_markdown(match.group(0)) + "\n\n",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    def replace_pre(match: re.Match) -> str:
        attrs = match.group(1) or ""
        code = match.group(2)
        lang_match = re.search(r"language-([a-zA-Z0-9_+\-.]+)", attrs)
        language = lang_match.group(1) if lang_match else ""
        code_text = unescape(re.sub(r"<[^>]+>", "", code)).strip("\n")
        return f"\n\n```{language}\n{code_text}\n```\n\n"

    text = re.sub(
        r"<pre[^>]*><code([^>]*)>(.*?)</code></pre>",
        replace_pre,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<code[^>]*>(.*?)</code>",
        lambda match: f"`{strip_tags(match.group(1))}`",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    def replace_anchor(match: re.Match) -> str:
        attrs = match.group(1) or ""
        content = strip_tags(match.group(2))
        href_match = re.search(r'href=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        href = href_match.group(1).strip() if href_match else ""

        if not content:
            return ""

        if href and not href.startswith("#"):
            return f"[{content}]({href})"

        return content

    text = re.sub(
        r"<a([^>]*)>(.*?)</a>",
        replace_anchor,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    for level in range(6, 0, -1):
        pattern = rf"<h{level}[^>]*>(.*?)</h{level}>"
        text = re.sub(
            pattern,
            lambda match, lvl=level: (
                f"\n\n{'#' * lvl} {strip_tags(match.group(1))}\n\n"
            ),
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )

    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</li>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "\n- ", text, flags=re.IGNORECASE)

    for tag in BLOCK_TAGS:
        text = re.sub(rf"<{tag}[^>]*>", "\n\n", text, flags=re.IGNORECASE)
        text = re.sub(rf"</{tag}>", "\n\n", text, flags=re.IGNORECASE)

    for tag in LIST_TAGS:
        text = re.sub(rf"<{tag}[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(rf"</{tag}>", "\n", text, flags=re.IGNORECASE)

    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = normalize_text(text)

    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("-"):
            stripped = re.sub(r"^-\s*", "- ", stripped)
        lines.append(stripped if stripped else "")

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_version() -> str:
    """Resolve the project version from package metadata or git tags."""
    try:
        return package_version("python-trueconf-bot")
    except PackageNotFoundError:
        pass
    except Exception as exc:  # pragma: no cover
        log.debug(f"llms-txt: Failed to read package metadata version: {exc}")

    try:
        return subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover
        log.debug(f"llms-txt: Failed to read git version: {exc}")

    return "dev"


def get_page_title(html: str, fallback: str) -> str:
    """Extract a human-readable page title from rendered HTML."""
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if h1_match:
        title = strip_tags(h1_match.group(1))
        if title:
            return title

    title_match = re.search(
        r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE
    )
    if title_match:
        raw_title = strip_tags(title_match.group(1))
        title = re.split(r"\s[-|–—]\s", raw_title)[0].strip()
        if title:
            return title

    slug = fallback.replace("index.html", "").strip("/")
    if not slug:
        return "Home"

    return slug.split("/")[-1].replace("-", " ").replace("_", " ").title()


def normalize_doc_path(doc_path: str) -> str:
    """Normalize a nav doc path into the corresponding rendered html path."""
    path = doc_path.replace("\\", "/").strip("/")

    if path.endswith(".md"):
        path = path[:-3]

    if not path or path == ".":
        return "index.html"

    if path.endswith("/index"):
        return f"{path}.html"

    return f"{path}/index.html"


def flatten_nav(nav_items) -> list[str]:
    """Flatten MkDocs nav config into ordered rendered html paths."""
    ordered_paths: list[str] = []

    def traverse(item) -> None:
        if isinstance(item, list):
            for nested in item:
                traverse(nested)
            return

        if isinstance(item, dict):
            for value in item.values():
                traverse(value)
            return

        if isinstance(item, str):
            ordered_paths.append(normalize_doc_path(item))

    traverse(nav_items or [])
    return ordered_paths


def get_section_key(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized == "index.html" or normalized.startswith(
        ("features/", "release_notes/")
    ):
        return "root"
    if normalized.startswith("learn/"):
        return "learn"
    if normalized.startswith("reference/"):
        return "reference"
    if normalized.startswith("examples/"):
        return "examples"
    return "other"


def path_sort_key(path: str, nav_positions: dict[str, int]):
    section = get_section_key(path)
    nav_position = nav_positions.get(path, 10**6)
    return (
        SECTION_ORDER.get(section, 99),
        nav_position,
        path.count("/"),
        path.lower(),
    )


def build_url(base_url: str, rel_path: str) -> str:
    """Build a public URL for a rendered html file."""
    normalized = rel_path.replace("\\", "/").lstrip("/")
    if normalized == "index.html":
        return f"{base_url}/index.md"

    if normalized.endswith("/index.html"):
        path_without_index = normalized[: -len("index.html")].rstrip("/")
        return f"{base_url}/{path_without_index}.md"

    return f"{base_url}/{normalized.rsplit('.', 1)[0]}.md"


def make_indent(level: int) -> str:
    return "  " * max(level, 0)


def add_index_entry(
    index_lines: list[str], title: str, url: str, level: int = 0
) -> None:
    index_lines.append(f"{make_indent(level)}- [{title}]({url})")


def build_index_lines(page_entries: list[dict]) -> list[str]:
    """Build the hierarchical INDEX section."""
    index_lines = ["## INDEX"]

    home_entry = next(
        (entry for entry in page_entries if entry["path"] == "index.html"), None
    )
    features_entry = next(
        (entry for entry in page_entries if entry["path"] == "features/index.html"),
        None,
    )
    release_notes_entry = next(
        (
            entry
            for entry in page_entries
            if entry["path"] == "release_notes/index.html"
        ),
        None,
    )

    if home_entry:
        add_index_entry(index_lines, home_entry["title"], home_entry["url"], level=0)
    if features_entry:
        add_index_entry(
            index_lines, features_entry["title"], features_entry["url"], level=0
        )

    grouped_sections = {"learn": [], "reference": [], "examples": []}
    for entry in page_entries:
        section = get_section_key(entry["path"])
        if section in grouped_sections:
            grouped_sections[section].append(entry)

    for section_key in ("learn", "reference", "examples"):
        entries = grouped_sections[section_key]
        if not entries:
            continue

        index_lines.append(f"- [{SECTION_LABELS[section_key]}](#{section_key})")
        for entry in entries:
            add_index_entry(index_lines, entry["title"], entry["url"], level=1)

    if release_notes_entry:
        add_index_entry(
            index_lines,
            release_notes_entry["title"],
            release_notes_entry["url"],
            level=0,
        )

    return index_lines


def write_lines(path: str, lines: list[str]) -> None:
    """Write text lines using UTF-8 encoding."""
    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(lines).strip() + "\n")


def on_post_build(config):
    """Generate llms.txt and llms-full.txt from rendered HTML files."""
    site_dir = config["site_dir"]
    base_url = (config.get("site_url") or "http://127.0.0.1:8000").rstrip("/")
    nav_paths = flatten_nav(config.get("nav", []))
    nav_positions = {path: idx for idx, path in enumerate(nav_paths)}

    discovered_paths = []
    for root, _, filenames in os.walk(site_dir):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), site_dir)
            rel_path = rel_path.replace("\\", "/")
            if should_include_page(rel_path):
                discovered_paths.append(rel_path)

    sorted_paths = sorted(
        set(discovered_paths), key=lambda path: path_sort_key(path, nav_positions)
    )

    page_entries = []
    for rel_path in sorted_paths:
        abs_path = os.path.join(site_dir, rel_path)

        try:
            with open(abs_path, "r", encoding="utf-8") as file_obj:
                html = file_obj.read()
        except Exception as exc:
            log.warning(f"llms-txt: Failed to read rendered HTML {rel_path}: {exc}")
            continue

        main_html = extract_main_content(html)
        markdown = html_to_markdown(main_html)
        title = get_page_title(html, rel_path)
        url = build_url(base_url, rel_path)

        if rel_path == "index.html":
            md_filename = "index.md"
        elif rel_path.endswith("/index.html"):
            md_filename = rel_path.replace("/index.html", ".md")
        else:
            md_filename = rel_path.rsplit(".", 1)[0] + ".md"
        md_rel_path = os.path.join(site_dir, md_filename)
        md_dir = os.path.dirname(md_rel_path)
        os.makedirs(md_dir, exist_ok=True)
        with open(md_rel_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown.strip() + "\n")

        page_entries.append(
            {
                "path": rel_path,
                "title": title,
                "url": url,
                "content": markdown,
            }
        )

    index_lines = build_index_lines(page_entries)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    version = get_version()

    llms_lines = [
        "# Python TrueConf Bot SDK",
        *index_lines,
        "",
        "## CONTENT",
        "See `llms-full.txt` for the complete rendered documentation.",
    ]

    full_lines = [
        "# Python TrueConf Bot SDK",
        "## METADATA",
        f"- **Version:** {version}",
        f"- **Generated:** {generated_at}",
        f"- **URL:** {base_url}/",
        "",
        "---",
        "",
        *index_lines,
        "",
        "---",
        "",
        "## CONTENT",
    ]

    for entry in page_entries:
        full_lines.extend(
            [
                "",
                f"# DOCUMENT: {entry['title']}",
                f"**Source:** {entry['url']}",
                "",
                entry["content"] or "_No content extracted._",
                "",
                "---",
            ]
        )

    write_lines(os.path.join(site_dir, "llms.txt"), llms_lines)
    write_lines(os.path.join(site_dir, "llms-full.txt"), full_lines)

    log.info("llms-txt: Generated llms.txt and llms-full.txt from rendered HTML")
