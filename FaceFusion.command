#!/usr/bin/env bash
# =============================================================================
# FaceFusion Quick Double-Click Launcher
# Just double-click this file in Finder!
# No Conda, No Pillow, No manual terminal commands needed.
# =============================================================================

cd "$(dirname "$0")" || exit 1

VENV_DIR=".venv"
VENV_PYTHON="$VENV_DIR/bin/python"

echo "============================================="
echo "🎭 FaceFusion Launcher"
echo "============================================="

if [ ! -f "$VENV_PYTHON" ]; then
    echo "First-time setup detected. Setting up FaceFusion..."
    echo "(This only happens once and takes a couple minutes)"
    echo ""

    # Find available python3
    PYTHON_CMD=""
    for cmd in python3.11 python3 /usr/local/bin/python3 /opt/homebrew/bin/python3 /usr/bin/python3; do
        if command -v "$cmd" >/dev/null 2>&1; then
            PYTHON_CMD="$cmd"
            break
        fi
    done

    if [ -z "$PYTHON_CMD" ]; then
        echo "Error: Python 3 was not found on your Mac."
        echo "Please install Python 3 from https://www.python.org/downloads/macos/"
        read -n 1 -s -r -p "Press any key to exit..."
        exit 1
    fi

    echo "Using: $($PYTHON_CMD --version)"
    echo "Creating private virtual environment..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"

    echo "Installing required packages..."
    "$VENV_PYTHON" -m pip install --upgrade pip --quiet
    "$VENV_PYTHON" install.py default --skip-conda

    echo ""
    echo "Setup finished! Starting FaceFusion..."
    echo ""
fi

echo "Starting FaceFusion..."
echo "Your web browser will open automatically."
echo "To stop FaceFusion when done, close this window or press Control + C."
echo ""

"$VENV_PYTHON" facefusion.py run --open-browser
