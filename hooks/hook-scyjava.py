from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

hiddenimports = collect_submodules("scyjava")
binaries = collect_dynamic_libs("scyjava")
