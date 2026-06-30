def on_page_content(html, page, config, files):
    raw_date = page.meta.get("git_revision_date_localized_raw_iso_date")
    if raw_date:
        page.update_date = raw_date