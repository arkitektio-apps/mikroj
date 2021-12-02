import os


MIKRO_J_PATH = os.path.dirname(os.path.realpath(__file__))

PLUGIN_PATH = os.getenv("MIKRO_J_PLUGINS_PATH", os.path.join(MIKRO_J_PATH, "plugins"))
MACROS_PATH = os.getenv("MIKRO_J_MACROS_PATH", os.path.join(MIKRO_J_PATH, "macros"))
ASSETS_PATH = os.path.join(MIKRO_J_PATH, "assets")


def get_asset_file(file, darkMode=False):
    return os.path.join(ASSETS_PATH, file)
