#!/usr/bin/env bash
# =============================================================================
# build.sh — Builds the FaceFusion.app macOS launcher
#
# Usage:
#   cd facefusion/launcher
#   bash build.sh
#
# The finished app will be at:
#   launcher/dist/FaceFusion.app
#
# Requirements (install once):
#   pip install rumps pyinstaller Pillow
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🎭 FaceFusion macOS Launcher Builder"
echo "====================================="

# ── 1. Check dependencies ────────────────────────────────────────────────────
echo ""
echo "▶ Checking build dependencies…"

for pkg in rumps PyInstaller PIL; do
    python3 -c "import $pkg" 2>/dev/null || {
        echo "  Installing $pkg…"
        pip install rumps pyinstaller Pillow --quiet
        break
    }
done

echo "  ✓ Dependencies OK"

# ── 2. Generate .icns icon ────────────────────────────────────────────────────
echo ""
echo "▶ Generating app icon…"
python3 "$SCRIPT_DIR/make_icon.py"
echo "  ✓ Icon created at resources/FaceFusion.icns"

# ── 3. Clean previous build ───────────────────────────────────────────────────
echo ""
echo "▶ Cleaning previous build…"
rm -rf "$SCRIPT_DIR/build" "$SCRIPT_DIR/dist"

# ── 4. Run PyInstaller ────────────────────────────────────────────────────────
echo ""
echo "▶ Building FaceFusion.app with PyInstaller…"
cd "$SCRIPT_DIR"
python3 -m PyInstaller FaceFusion.spec --noconfirm

# ── 5. Done ───────────────────────────────────────────────────────────────────
APP_PATH="$SCRIPT_DIR/dist/FaceFusion.app"

if [ -d "$APP_PATH" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "   App location: $APP_PATH"
    echo ""
    echo "   To install: drag FaceFusion.app to your Applications folder"
    echo "   To run now: open \"$APP_PATH\""
    echo ""
    # Optionally open the dist folder in Finder
    open "$SCRIPT_DIR/dist"
else
    echo ""
    echo "❌ Build failed — FaceFusion.app not found in dist/"
    exit 1
fi
