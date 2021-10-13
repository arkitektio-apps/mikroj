import os


MIKRO_J_PATH = os.path.dirname(os.path.realpath(__file__))

PLUGIN_PATH = os.getenv("MIKRO_J_PLUGINS_PATH", MIKRO_J_PATH + "/plugins")