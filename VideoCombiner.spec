# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['.\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# --- ADD THIS LINE TO FILTER OUT TZDATA ---
a.datas = [entry for entry in a.datas if not entry[0].startswith('tzdata')]
# -------------------------------------------

pyz = PYZ(a.pure)
splash = Splash(
    'CalvinPatch_CDC.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(30, 470),
    text_size=12,
    text_font='Helvetica',   # Font name
    text_color='#000000',     # Font color (HEX)
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [],
    name='Cirrus Video Veiwer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['video.png'],
)
