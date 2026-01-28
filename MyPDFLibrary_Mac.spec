# -*- mode: python ; coding: utf-8 -*-

# MyPDFLibrary_Mac.spec
# Mac용 PyInstaller 설정 파일

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MyPDFLibrary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Mac 앱은 콘솔 없음
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/book.icns', # Mac용 아이콘 (변환된 파일 사용)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyPDFLibrary',
)

app = BUNDLE(
    coll,
    name='MyPDFLibrary.app',
    icon='assets/book.icns',
    bundle_identifier='com.yoon.mypdflibrary',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
        'CFBundleShortVersionString': '1.0.5',
        'CFBundleVersion': '1.0.5',
    },
)
