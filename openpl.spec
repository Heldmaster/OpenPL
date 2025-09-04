# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/cmd/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/', 'src/'),
           ('src/cfg/config.toml', '.')],
    hiddenimports=['pymavlink.dialects.v20',
                   'pymavlink.dialects.v20.common', 
                   'pymavlink.dialects.v20.ardupilotmega', 
                   'pymavlink.dialects.v20.all', 
                   'pymavlink.mavutil',
                   'cv2',
                   'imagezmq',
                   'toml',
                   'vidgear',
                   'vidgear.gears',
                   'pupil_apriltags',
                   ],
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
    [],
    exclude_binaries=True,
    name='opl-core',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='opl-core',
)
