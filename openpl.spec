# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import site
import glob
import shutil

NAME = "opl-core"

def find_package_lib_paths(package_name):
    site_packages_paths = site.getsitepackages()
    if not site_packages_paths:
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_packages_paths = [os.path.join(sys.prefix, 'lib', python_version, 'site-packages')]
    
    site_packages_paths.append(site.getusersitepackages())
    
    for path in site_packages_paths:
        if not os.path.exists(path):
            continue
            
        package_path = os.path.join(path, package_name)
        if os.path.exists(package_path):
            lib_path = os.path.join(package_path, 'lib')
            lib64_path = os.path.join(package_path, 'lib64')
            
            result = []
            if os.path.exists(lib_path):
                result.append((lib_path, os.path.join(package_name, 'lib')))
            if os.path.exists(lib64_path):
                result.append((lib64_path, os.path.join(package_name, 'lib64')))
                
            if result:
                return result
            
        pattern = os.path.join(path, package_name + '*')
        for match in glob.glob(pattern):
            if os.path.isdir(match):
                lib_path = os.path.join(match, 'lib')
                lib64_path = os.path.join(match, 'lib64')
                
                result = []
                if os.path.exists(lib_path):
                    result.append((lib_path, os.path.join(package_name, 'lib')))
                if os.path.exists(lib64_path):
                    result.append((lib64_path, os.path.join(package_name, 'lib64')))
                    
                if result:
                    return result
    
    return []

pupil_apriltags_lib_paths = find_package_lib_paths('pupil_apriltags')

datas_list = [('src/', 'src/'),
              ('config.toml', '.')]

for src_path, dest_path in pupil_apriltags_lib_paths:
    print(f"Found {src_path}, adding to datas as {dest_path}")
    datas_list.append((src_path, dest_path))

if not pupil_apriltags_lib_paths:
    print("WARNING: pupil_apriltags lib directories not found")

a = Analysis(
    ['src/cmd/main.py'],
    pathex=[],
    binaries=[],
    datas=datas_list,
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
                   'pyserial',
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
    name=NAME,
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
    name=NAME,
)

def copy_root_config():
    root_config = os.path.join('config.toml')
    
    deploy_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    dist_dir = os.path.join(deploy_dir, 'dist', NAME)
    
    if os.path.exists(root_config):
        print(f"Copying root config.toml to {dist_dir}")
        shutil.copy2(root_config, dist_dir)
    else:
        print("WARNING: Root config.toml not found")

copy_root_config()