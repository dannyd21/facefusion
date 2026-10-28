#!/usr/bin/env python3
"""
FaceFusion macOS Launcher
A menu-bar app that manages the FaceFusion Gradio server.
"""

import os
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

import rumps

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

APP_NAME = 'FaceFusion'
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 7860
SERVER_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'
STARTUP_TIMEOUT = 60  # seconds to wait for Gradio to be ready

# Resolve the FaceFusion root (one level up from this file's directory)
LAUNCHER_DIR = Path(__file__).resolve().parent
FACEFUSION_ROOT = LAUNCHER_DIR.parent

# Icons (using emoji as fallback — replaced by .icns at bundle time)
ICON_IDLE = None       # uses the .icns set in the spec
ICON_LOADING = None
ICON_RUNNING = None
ICON_ERROR = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_python() -> str:
    """
    Find python executable without requiring Conda.
    1. Frozen app (bundled inside .app)
    2. Local .venv inside facefusion folder
    3. Conda environment if available
    4. System python3 / python
    """
    if getattr(sys, 'frozen', False):
        return sys.executable

    # Check local standalone virtualenv
    local_venvs = [
        FACEFUSION_ROOT / '.venv' / 'bin' / 'python',
        FACEFUSION_ROOT / 'venv' / 'bin' / 'python',
        FACEFUSION_ROOT / '.venv' / 'bin' / 'python3',
    ]
    for candidate in local_venvs:
        if candidate.is_file():
            return str(candidate)

    # Check conda if installed
    conda_root = os.getenv('CONDA_PREFIX_1') or os.getenv('CONDA_ROOT') or _detect_conda_root()
    if conda_root:
        candidates = [
            os.path.join(conda_root, 'envs', 'facefusion', 'bin', 'python'),
            os.path.join(conda_root, 'envs', 'facefusion', 'bin', 'python3'),
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                return candidate

    # Try shutil / PATH lookup as last resort
    import shutil
    return shutil.which('python3') or shutil.which('python') or sys.executable


def _detect_conda_root() -> str:
    """Try to find conda's base prefix from common install locations."""
    home = Path.home()
    candidates = [
        home / 'miniconda3',
        home / 'anaconda3',
        home / 'miniforge3',
        home / 'mambaforge',
        Path('/opt/homebrew/Caskroom/miniconda/base'),
        Path('/usr/local/Caskroom/miniconda/base'),
        Path('/opt/miniconda3'),
        Path('/opt/anaconda3'),
    ]
    for path in candidates:
        if path.is_dir():
            return str(path)
    return ''


def is_server_ready() -> bool:
    """Return True if the Gradio server is accepting connections."""
    import urllib.request
    try:
        urllib.request.urlopen(SERVER_URL, timeout=2)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main app class
# ---------------------------------------------------------------------------

class FaceFusionApp(rumps.App):

    def __init__(self):
        super().__init__(
            name=APP_NAME,
            title='🎭',
            quit_button=None,   # we add our own so we can clean up first
        )

        self._server_process: subprocess.Popen | None = None
        self._monitor_thread: threading.Thread | None = None
        self._starting = False

        # Build menu
        self.open_item   = rumps.MenuItem('Open FaceFusion', callback=self.open_browser)
        self.status_item = rumps.MenuItem('Status: Stopped')
        self.start_item  = rumps.MenuItem('Start Server',   callback=self.start_server)
        self.stop_item   = rumps.MenuItem('Stop Server',    callback=self.stop_server)
        self.quit_item   = rumps.MenuItem('Quit',           callback=self.quit_app)

        self.open_item.set_callback(None)  # disabled until running
        self.stop_item.set_callback(None)  # disabled until running

        self.menu = [
            self.open_item,
            None,                           # separator
            self.status_item,
            None,
            self.start_item,
            self.stop_item,
            None,
            self.quit_item,
        ]

        self._pending_status = None

        # Poll for pending status updates on the main thread every 0.25 s
        rumps.Timer(self._apply_pending_status, 0.25).start()

        # Auto-start on launch
        rumps.Timer(self._auto_start, 0.5).start()

    # ------------------------------------------------------------------
    # Server lifecycle
    # ------------------------------------------------------------------

    def _auto_start(self, _timer):
        """Called once shortly after the app starts."""
        _timer.stop()
        self.start_server(None)

    def start_server(self, _sender):
        if self._server_process and self._server_process.poll() is None:
            return  # already running
        if self._starting:
            return

        self._starting = True
        self._set_status('Starting…', loading=True)
        self.start_item.set_callback(None)

        thread = threading.Thread(target=self._launch_server, daemon=True)
        thread.start()

    def _launch_server(self):
        python = find_python()
        facefusion_py = str(FACEFUSION_ROOT / 'facefusion.py')

        cmd = [python, facefusion_py, 'run',
               '--server-host', SERVER_HOST,
               '--server-port', str(SERVER_PORT)]

        env = os.environ.copy()
        env['SYSTEM_VERSION_COMPAT'] = '0'

        try:
            self._server_process = subprocess.Popen(
                cmd,
                cwd=str(FACEFUSION_ROOT),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except Exception as exc:
            self._set_status(f'Error: {exc}', error=True)
            self._starting = False
            self.start_item.set_callback(self.start_server)
            return

        # Wait for server to become ready
        deadline = time.time() + STARTUP_TIMEOUT
        while time.time() < deadline:
            if self._server_process.poll() is not None:
                self._set_status('Server exited unexpectedly', error=True)
                self._starting = False
                self.start_item.set_callback(self.start_server)
                return
            if is_server_ready():
                break
            time.sleep(1)
        else:
            self._set_status('Timed out waiting for server', error=True)
            self._starting = False
            self.start_item.set_callback(self.start_server)
            return

        self._starting = False
        self._set_status('Running', running=True)
        webbrowser.open(SERVER_URL)

        # Start background monitor
        self._monitor_thread = threading.Thread(target=self._monitor_server, daemon=True)
        self._monitor_thread.start()

    def _monitor_server(self):
        """Watch the server process; update status if it dies."""
        while self._server_process and self._server_process.poll() is None:
            time.sleep(2)
        if not self._starting:
            self._set_status('Stopped')

    def stop_server(self, _sender):
        if self._server_process and self._server_process.poll() is None:
            self._server_process.terminate()
            try:
                self._server_process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self._server_process.kill()
        self._server_process = None
        self._set_status('Stopped')

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _set_status(self, text: str, running=False, loading=False, error=False):
        """Update menu items to reflect current state (called from any thread)."""
        # Store desired state so the main-thread timer can apply it safely
        self._pending_status = dict(text=text, running=running, loading=loading, error=error)

    def _apply_pending_status(self, _timer):
        """Called on the main thread by a one-shot timer."""
        state = getattr(self, '_pending_status', None)
        if state is None:
            return

        self._pending_status = None
        text    = state['text']
        running = state['running']
        loading = state['loading']
        error   = state['error']

        self.status_item.title = f'Status: {text}'

        if running:
            self.title = '🎭'
            self.open_item.set_callback(self.open_browser)
            self.stop_item.set_callback(self.stop_server)
            self.start_item.set_callback(None)
        elif loading:
            self.title = '⏳'
            self.open_item.set_callback(None)
            self.stop_item.set_callback(None)
            self.start_item.set_callback(None)
        elif error:
            self.title = '⚠️'
            self.open_item.set_callback(None)
            self.stop_item.set_callback(None)
            self.start_item.set_callback(self.start_server)
        else:  # stopped
            self.title = '🎭'
            self.open_item.set_callback(None)
            self.stop_item.set_callback(None)
            self.start_item.set_callback(self.start_server)

    def open_browser(self, _sender):
        webbrowser.open(SERVER_URL)

    # ------------------------------------------------------------------
    # Quit
    # ------------------------------------------------------------------

    def quit_app(self, _sender):
        self.stop_server(None)
        rumps.quit_application()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    FaceFusionApp().run()
