# -*- mode: python ; coding: utf-8 -*-

import os
from os.path import join, dirname, exists, abspath
import importlib
import sys

NAME = 'RedditDownloader'

project_base = abspath('./')

package_imports = {
    'eel': ['eel.js'],
    'newspaper': [''],
    'praw': ['praw.ini'],
    'pip': ['']
}

datas = [
    ('./redditdownloader/sql/alembic_files', 'sql/alembic_files'),
    ('./redditdownloader/web', 'web/'),
    ('./redditdownloader/tests', 'tests')
]

for package, files in package_imports.items():
    proot = dirname(importlib.import_module(package).__file__)
    print('Found package data:', package, proot)
    datas.extend((join(proot, f), package) for f in files)

for d in datas:
    print('\t+', d, os.path.exists(d[0]))


block_cipher = None

print('Project base:', project_base)


a = Analysis(['Run.py'],
             pathex=['./redditdownloader', project_base],
             binaries=[],
             datas=datas,
             hiddenimports=['bottle_websocket', './redditdownloader', 'sqlalchemy.ext.baked'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['nltk'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name=NAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon='./redditdownloader/web/img/logo.ico')
