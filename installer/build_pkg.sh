#!/usr/bin/env bash
# =============================================================================
# build_pkg.sh — Generates the native macOS FaceFusion-Installer.pkg
#
# Requirements on macOS:
#   pkgbuild & productbuild (included standard on all Macs)
#
# Usage:
#   cd installer
#   bash build_pkg.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
APP_SOURCE="$REPO_ROOT/FaceFusion.app"
OUTPUT_DIR="$REPO_ROOT/dist"

echo "============================================="
echo "📦 FaceFusion .pkg Installer Builder"
echo "============================================="

# Ensure app exists
if [ ! -d "$APP_SOURCE" ]; then
    echo "Error: FaceFusion.app not found at $APP_SOURCE"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo ""
echo "▶ 1. Building Component Package (pkgbuild)..."
pkgbuild \
    --component "$APP_SOURCE" \
    --install-location "/Applications" \
    --identifier "io.facefusion.pkg" \
    --version "3.9.2" \
    --scripts "$SCRIPT_DIR/scripts" \
    "$TMP_DIR/FaceFusion-component.pkg"

echo ""
echo "▶ 2. Building Final Distribution Package (productbuild)..."
productbuild \
    --distribution "$SCRIPT_DIR/distribution.xml" \
    --resources "$SCRIPT_DIR/resources" \
    --package-path "$TMP_DIR" \
    "$OUTPUT_DIR/FaceFusion-Installer.pkg"

echo ""
echo "============================================="
echo "✅ Successfully built:"
echo "   $OUTPUT_DIR/FaceFusion-Installer.pkg"
echo "============================================="
