# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app_launcher_cli.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['json_to_file', 'json_to_file.source_to_json', 'json_to_file.markdown_export', 'json_to_file.pdf_export', 'json_to_file.word_export', 'json_to_file.utils', 'tkinter', 'tkinter.filedialog'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DocGenius',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
