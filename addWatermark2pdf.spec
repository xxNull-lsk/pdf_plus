# -*- mode: python -*-

block_cipher = None


a = Analysis(['addWatermark2pdf.py'],
             pathex=['D:\\CodeProjects\\PDF_Plus_Watermark'],
             binaries=[],
             datas=[('./res', './res')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

'''
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Cloudown',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='./res/app.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main-gui')
'''			   
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='addWatermark2pdf',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='./res/app.ico')