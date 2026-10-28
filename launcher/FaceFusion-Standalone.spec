# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for completely standalone FaceFusion macOS app.
Packages FaceFusion, Gradio, OpenCV, ONNX Runtime, and the launcher
into a single self-contained FaceFusion.app bundle.
No Conda, no external Python, and no terminal required for end users.
"""

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

SPECPATH_DIR = Path(SPECPATH).resolve()
LAUNCHER_DIR = SPECPATH_DIR if SPECPATH_DIR.name == 'launcher' else SPECPATH_DIR / 'launcher'
ROOT = LAUNCHER_DIR.parent

# Collect all dynamic FaceFusion submodules so importlib finds them
facefusion_submodules = collect_submodules('facefusion')
gradio_submodules = collect_submodules('gradio')
gradio_rangeslider_submodules = collect_submodules('gradio_rangeslider')

# Collect all data files (CSS, templates, static web assets)
gradio_datas = collect_data_files('gradio')
gradio_rangeslider_datas = collect_data_files('gradio_rangeslider')

datas = [
    (str(ROOT / 'facefusion'), 'facefusion'),
    (str(ROOT / 'facefusion.ini'), '.'),
    (str(LAUNCHER_DIR / 'resources' / 'FaceFusion.icns'), 'resources'),
] + gradio_datas + gradio_rangeslider_datas

hiddenimports = list(set(
    facefusion_submodules +
    gradio_submodules +
    gradio_rangeslider_submodules +
    [
        'rumps',
        'onnxruntime',
        'cv2',
        'numpy',
        'scipy',
        'tqdm',
        'urllib.request',
        'multiprocessing',
        'inspect',
        'json',
        'shutil',
    ]
))

a = Analysis(
    [str(LAUNCHER_DIR / 'app.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'torch'],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    icon=str(LAUNCHER_DIR / 'resources' / 'FaceFusion.icns'),
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
    icon=str(LAUNCHER_DIR / 'resources' / 'FaceFusion.icns'),
    bundle_identifier='io.facefusion.app',
    info_plist={
        'CFBundleName': 'FaceFusion',
        'CFBundleDisplayName': 'FaceFusion',
        'CFBundleVersion': '3.9.2',
        'CFBundleShortVersionString': '3.9.2',
        'NSHighResolutionCapable': True,
        'LSUIElement': True,  # Runs in menu bar, no dock clutter
        'NSRequiresAquaSystemAppearance': False,
    },
)
