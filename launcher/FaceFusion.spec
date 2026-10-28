# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the FaceFusion macOS launcher app.
Run with:  pyinstaller FaceFusion.spec
"""

import os
from pathlib import Path

ROOT = Path(SPECPATH).parent          # facefusion repo root
LAUNCHER = Path(SPECPATH)             # launcher/ directory

a = Analysis(
    [str(LAUNCHER / 'app.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Bundle the FaceFusion icon
        (str(LAUNCHER / 'resources' / 'FaceFusion.icns'), 'resources'),
    ],
    hiddenimports=[
        'rumps',
        'urllib.request',
        'threading',
        'subprocess',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Keep the bundle lean — these are only needed in the server process
        'gradio', 'numpy', 'cv2', 'onnxruntime',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FaceFusion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,      # no terminal window
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(LAUNCHER / 'resources' / 'FaceFusion.icns'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='FaceFusion',
)

app = BUNDLE(
    coll,
    name='FaceFusion.app',
    icon=str(LAUNCHER / 'resources' / 'FaceFusion.icns'),
    bundle_identifier='io.facefusion.launcher',
    info_plist={
        'CFBundleName': 'FaceFusion',
        'CFBundleDisplayName': 'FaceFusion',
        'CFBundleVersion': '3.9.2',
        'CFBundleShortVersionString': '3.9.2',
        'NSHighResolutionCapable': True,
        'LSUIElement': True,        # menu-bar only app, no Dock icon
        'NSRequiresAquaSystemAppearance': False,
    },
)
