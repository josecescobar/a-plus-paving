"""Sync header nav and footer from index.html to all other pages.

Usage: python3 sync-nav-footer.py

Uses index.html as the source of truth. Extracts the <header>...</header>
and <footer>...</footer> blocks and replaces them in all other HTML files,
adjusting relative paths (e.g., href="x" → href="../x") for blog/ pages.

The active-page highlight (text-custom-green font-semibold) is preserved
per page based on the page's own filename.
"""
import os
import re
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))

# Map each page to which nav link should be highlighted
NAV_ACTIVE = {
    "index.html": "index.html",
    "services.html": "services.html",
    "gallery.html": "gallery.html",
    "about.html": "about.html",
    "contact.html": "contact.html",
    "blog.html": None,  # no nav link for blog
    "faq.html": None,
    "service-area.html": None,
    "404.html": None,
}

FOOTER_ACTIVE = {
    "index.html": "index.html",
    "services.html": "services.html",
    "gallery.html": "gallery.html",
    "about.html": "about.html",
    "contact.html": "contact.html",
    "blog.html": "blog.html",
    "faq.html": "faq.html",
    "service-area.html": "service-area.html",
    "404.html": None,
}

BLOG_NAV_ACTIVE = None  # blog posts don't highlight any nav item
BLOG_FOOTER_ACTIVE = "blog.html"

ACTIVE_NAV_CLASSES = "text-custom-green font-semibold hover:text-custom-green"
INACTIVE_NAV_CLASSES = "text-gray-700 hover:text-custom-green"

ACTIVE_FOOTER_CLASSES = "text-custom-green font-semibold hover:text-custom-green"
INACTIVE_FOOTER_CLASSES = "hover:text-custom-green"


def extract_block(html, tag):
    """Extract a block like <header>...</header> from HTML."""
    pattern = re.compile(
        rf'([ \t]*)<{tag}\b[^>]*>.*?</{tag}>',
        re.DOTALL
    )
    m = pattern.search(html)
    if not m:
        raise ValueError(f"Could not find <{tag}> block")
    return m.group(0)


def adjust_paths_for_blog(block):
    """Convert href="x.html" to href="../x.html" and similar for blog/ pages."""
    # Adjust href and src paths (but not external URLs or anchors)
    block = re.sub(
        r'(href|src|srcset)="(?!https?://|mailto:|tel:|#|/)((?!\.\./)([^"]+))"',
        r'\1="../\3"',
        block
    )
    return block


def set_active_link(block, active_href, is_nav=True):
    """Set the active page highlight in nav or footer links."""
    if is_nav:
        active = ACTIVE_NAV_CLASSES
        inactive = INACTIVE_NAV_CLASSES
    else:
        active = ACTIVE_FOOTER_CLASSES
        inactive = INACTIVE_FOOTER_CLASSES

    # First, reset all links to inactive
    block = block.replace(active, inactive)

    # Then set the active link
    if active_href:
        # Find the link with matching href and make it active
        def activate(m):
            href = m.group(1)
            classes = m.group(2)
            basename = os.path.basename(href)
            if basename == active_href:
                new_classes = classes.replace(inactive, active)
                return f'href="{href}" class="{new_classes}'
            return m.group(0)

        # Match href="...something.html" followed by class="..."
        block = re.sub(
            r'href="([^"]*)" class="([^"]*' + re.escape(inactive) + r'[^"]*)',
            activate,
            block
        )

    return block


def replace_block(html, tag, new_block):
    """Replace a <tag>...</tag> block in HTML."""
    pattern = re.compile(
        rf'([ \t]*)<{tag}\b[^>]*>.*?</{tag}>',
        re.DOTALL
    )
    return pattern.sub(new_block, html, count=1)


def process():
    # Read source of truth
    with open(os.path.join(ROOT, "index.html")) as f:
        source = f.read()

    header_block = extract_block(source, "header")
    footer_block = extract_block(source, "footer")

    # Process all HTML files
    html_files = sorted(glob.glob(os.path.join(ROOT, "*.html")))
    html_files += sorted(glob.glob(os.path.join(ROOT, "blog", "*.html")))

    for filepath in html_files:
        basename = os.path.basename(filepath)
        reldir = os.path.relpath(os.path.dirname(filepath), ROOT)
        is_blog = reldir == "blog"

        if basename == "index.html" and not is_blog:
            continue  # skip source of truth

        with open(filepath) as f:
            html = f.read()

        # Check if file has header/footer blocks
        if "<header" not in html or "<footer" not in html:
            print(f"  Skipped: {os.path.relpath(filepath, ROOT)} (missing header/footer)")
            continue

        # Prepare header
        new_header = header_block
        if is_blog:
            nav_active = BLOG_NAV_ACTIVE
            new_header = adjust_paths_for_blog(new_header)
        else:
            nav_active = NAV_ACTIVE.get(basename)

        new_header = set_active_link(new_header, nav_active, is_nav=True)

        # Prepare footer
        new_footer = footer_block
        if is_blog:
            footer_active = BLOG_FOOTER_ACTIVE
            new_footer = adjust_paths_for_blog(new_footer)
        else:
            footer_active = FOOTER_ACTIVE.get(basename)

        new_footer = set_active_link(new_footer, footer_active, is_nav=False)

        # Replace blocks
        new_html = replace_block(html, "header", new_header)
        new_html = replace_block(new_html, "footer", new_footer)

        if new_html != html:
            with open(filepath, "w") as f:
                f.write(new_html)
            print(f"  Synced:  {os.path.relpath(filepath, ROOT)}")
        else:
            print(f"  OK:      {os.path.relpath(filepath, ROOT)} (already in sync)")


if __name__ == "__main__":
    print("=== Syncing nav & footer from index.html ===\n")
    process()
    print("\nDone.")
