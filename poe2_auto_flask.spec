# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 打包設定：執行 build.bat 產生 dist\POE2_AutoFlask\

from PyInstaller.utils.hooks import collect_all

block_cipher = None

pyqt_datas, pyqt_binaries, pyqt_hidden = collect_all("PyQt6")
mss_datas, mss_binaries, mss_hidden = collect_all("mss")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=pyqt_binaries + mss_binaries,
    datas=pyqt_datas + mss_datas,
    hiddenimports=[
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        "pydirectinput",
        "numpy",
    ]
    + pyqt_hidden
    + mss_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="POE2_AutoFlask",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="POE2_AutoFlask",
)
