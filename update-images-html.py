"""Update all HTML files: wrap <img> in <picture> with WebP, add width/height, update preloads."""
import re
import os
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))

# Image dimensions (post-optimization)
DIMS = {
    "6B495C08-D4D2-4FAF-A08B-232DC4281514.jpeg": (1400, 1399),
    "asphalt-overlay-3inch-roller.jpg": (569, 1200),
    "concrete-patio-installation.jpg": (960, 960),
    "driveway_commercial_parkinglot_20250424.jpg": (444, 320),
    "driveway_extension_sideyard_2024.jpg": (911, 1200),
    "driveway_longcurved_residential_2024.jpg": (1104, 828),
    "driveway_residential_curvedentry_20250424.jpg": (675, 345),
    "driveway_residential_front_20250424.jpg": (886, 1400),
    "driveway_residential_front_20250602.jpg": (1223, 800),
    "driveway_residential_garagefront_20250424.jpg": (828, 1104),
    "driveway_residential_padextension_20250424.jpg": (900, 1200),
    "driveway_residential_rollerwork_20250424.jpg": (784, 444),
    "driveway_residential_sideyard_20250424.jpg": (887, 442),
    "driveway_residential_stoneborder_20250424.jpg": (351, 618),
    "driveway_residential_stonewalk_20250424.jpg": (337, 618),
    "driveway_residential_streetview_2024.jpg": (346, 628),
    "driveway_residential_triplex_20250424.jpg": (659, 344),
    "driveway_residential_woodedcurve_20250424.jpg": (720, 960),
    "driveway_sealcoating_mainarea_20250424.jpg": (1284, 944),
    "driveway_tarandchip_residential_2024.jpg": (1146, 1400),
    "driveway_woodedcurve_residential_2024.jpg": (786, 1400),
    "driveway-grading-skid-steer.jpg": (903, 1200),
    "excavation-kubota-backhoe.jpg": (894, 1200),
    "fresh-asphalt-driveway-installation.jpg": (512, 800),
    "front-garden-bed-transformation.jpg": (960, 960),
    "parkinglot_commercial_striping_2024.jpg": (1284, 953),
    "porch-landscaping-makeover.jpg": (960, 960),
    "road_repair.jpg": (870, 1400),
    "road-repair-saw-cutting.jpg": (746, 1200),
}

def webp_name(jpg_path):
    """Convert images/foo.jpg -> images/foo.webp"""
    base, _ = os.path.splitext(jpg_path)
    return base + ".webp"

def get_dims(filename):
    """Look up width, height for a filename."""
    return DIMS.get(filename, (None, None))

def process_img_tag(match):
    """Wrap an <img> tag in <picture> with WebP source and add width/height."""
    full_tag = match.group(0)

    # Extract src
    src_match = re.search(r'src="([^"]*)"', full_tag)
    if not src_match:
        return full_tag
    src = src_match.group(1)

    # Only process images/ references
    if "images/" not in src:
        return full_tag

    # Get filename
    filename = os.path.basename(src)
    w, h = get_dims(filename)

    # Build WebP srcset path
    webp_src = webp_name(src)

    # Detect indentation from the line
    line_start = match.string.rfind("\n", 0, match.start())
    if line_start == -1:
        indent = ""
    else:
        line_content = match.string[line_start+1:match.start()]
        indent = re.match(r'^(\s*)', line_content).group(1)

    # Add width/height if we have dimensions and they're not already there
    img_tag = full_tag
    if w and h and 'width=' not in full_tag:
        # Insert width/height before the closing >
        img_tag = re.sub(r'\s*/?>$', f' width="{w}" height="{h}">', img_tag.rstrip())
        if img_tag.endswith(">>"):
            img_tag = img_tag[:-1]

    # Wrap in <picture>
    result = f'<picture>\n{indent}    <source srcset="{webp_src}" type="image/webp">\n{indent}    {img_tag}\n{indent}</picture>'
    return result

def process_preload(match):
    """Update preload tags to use WebP."""
    full_tag = match.group(0)
    href_match = re.search(r'href="([^"]*)"', full_tag)
    if not href_match:
        return full_tag
    href = href_match.group(1)
    if "images/" not in href:
        return full_tag

    webp_href = webp_name(href)
    # Add imagesrcset for WebP with fallback
    return f'<link rel="preload" as="image" href="{webp_href}" type="image/webp">'

def process_background_image(match):
    """Update inline background-image to use WebP."""
    full = match.group(0)
    url_match = re.search(r"url\('([^']*)'\)", full)
    if not url_match:
        return full
    url = url_match.group(1)
    if "images/" not in url:
        return full
    webp_url = webp_name(url)
    return full.replace(url, webp_url)

def process_file(filepath):
    """Process a single HTML file."""
    with open(filepath, 'r') as f:
        content = f.read()

    original = content

    # 1. Wrap <img> tags that reference images/ in <picture>
    # Skip img tags already inside a <picture> element
    def wrap_if_unwrapped(match):
        # Check if this <img> is preceded by a <picture> tag (i.e. already wrapped)
        before = content[:match.start()]
        last_picture_open = before.rfind('<picture>')
        last_picture_close = before.rfind('</picture>')
        if last_picture_open > last_picture_close:
            return match.group(0)
        return process_img_tag(match)

    content = re.sub(
        r'<img\s[^>]*src="[^"]*images/[^"]*"[^>]*>',
        wrap_if_unwrapped,
        content
    )

    # 2. Update preload tags
    content = re.sub(
        r'<link\s+rel="preload"\s+as="image"\s+href="[^"]*images/[^"]*">',
        process_preload,
        content
    )

    # 3. Update background-image inline styles
    content = re.sub(
        r'style="background-image:\s*url\(\'[^\']*images/[^\']*\'\);"',
        process_background_image,
        content
    )

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  Updated: {os.path.relpath(filepath, ROOT)}")
    else:
        print(f"  Skipped: {os.path.relpath(filepath, ROOT)} (no changes)")

if __name__ == "__main__":
    html_files = glob.glob(os.path.join(ROOT, "*.html"))
    html_files += glob.glob(os.path.join(ROOT, "blog", "*.html"))

    print("=== Updating HTML files with <picture> elements ===\n")
    for f in sorted(html_files):
        process_file(f)
    print("\nDone.")
