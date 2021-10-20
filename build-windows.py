import PyInstaller.__main__

APP_NAME = "MikroJ"

PyInstaller.__main__.run([
    'entrypoint.py',
    '--clean',
    '--windowed',
    f'--name={APP_NAME}',
    '--noconfirm',
    '--add-data=share;share',
    '--additional-hooks-dir=hooks',
    '--icon=mikroj-logo.ico'
])