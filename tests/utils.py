import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MACROS_DIR = os.path.join(THIS_DIR, "macros")


def get_macro(image_name, macros_dir=MACROS_DIR):
    with open(os.path.join(macros_dir, image_name), "r") as f:
        return f.read()
