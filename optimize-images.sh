#!/bin/bash
# optimize-images.sh — Resize oversized images and create WebP versions
# Requires: sips (macOS built-in), cwebp (brew install webp)
#
# Usage: bash optimize-images.sh
#
# This script:
#   1. Resizes any image whose longest side exceeds MAX_DIM
#   2. Creates a .webp copy of every .jpg/.jpeg in images/

set -euo pipefail

IMG_DIR="$(cd "$(dirname "$0")" && pwd)/images"
MAX_DIM=1400      # max pixels on longest side (2x of ~700px display width)
WEBP_QUALITY=78   # good balance of size vs quality

if ! command -v cwebp &>/dev/null; then
  echo "Error: cwebp not found. Install with: brew install webp"
  exit 1
fi

echo "=== Image Optimization ==="
echo ""

total_before=0
total_after=0

for img in "$IMG_DIR"/*.jpg "$IMG_DIR"/*.jpeg; do
  [ -f "$img" ] || continue

  basename="$(basename "$img")"
  name="${basename%.*}"
  webp_out="$IMG_DIR/$name.webp"

  # Get current dimensions
  w=$(sips -g pixelWidth "$img" | awk '/pixelWidth/{print $2}')
  h=$(sips -g pixelHeight "$img" | awk '/pixelHeight/{print $2}')
  before_size=$(stat -f%z "$img")
  total_before=$((total_before + before_size))

  # Resize if either dimension exceeds MAX_DIM
  if [ "$w" -gt "$MAX_DIM" ] || [ "$h" -gt "$MAX_DIM" ]; then
    if [ "$w" -ge "$h" ]; then
      new_w=$MAX_DIM
      new_h=$(( h * MAX_DIM / w ))
    else
      new_h=$MAX_DIM
      new_w=$(( w * MAX_DIM / h ))
    fi
    echo "  RESIZE $basename: ${w}x${h} → ${new_w}x${new_h}"
    sips --resampleHeightWidth "$new_h" "$new_w" "$img" --out "$img" >/dev/null 2>&1
  fi

  # Convert to WebP
  cwebp -q "$WEBP_QUALITY" "$img" -o "$webp_out" -quiet 2>/dev/null

  after_size=$(stat -f%z "$webp_out")
  total_after=$((total_after + after_size))
  savings=$(( (before_size - after_size) * 100 / before_size ))

  printf "  %-55s %6dK → %6dK  (%2d%% saved)\n" \
    "$basename" $((before_size/1024)) $((after_size/1024)) "$savings"
done

echo ""
echo "Total JPEG: $((total_before/1024))K"
echo "Total WebP: $((total_after/1024))K"
echo "Overall savings: $(( (total_before - total_after) * 100 / total_before ))%"
echo ""
echo "Done. WebP files created alongside originals in images/"
