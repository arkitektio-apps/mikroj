import abc
import os
import sys
from arkitekt.agents.base import BaseAgent
from arkitekt.compositions.base import Arkitekt
from arkitekt.messages import Provision
from arkitekt.qt.magic_bar import MagicBar
from fakts.fakts import Fakts
from fakts.grants.qt.qtbeacon import QtSelectableBeaconGrant, SelectBeaconWidget
from herre.fakts.herre import FaktsHerre
from koil.composition.qt import QtPedanticKoil
from mikro.api.schema import RepresentationFragment
from mikro.arkitekt import ConnectedApp
from PyQt5 import QtCore, QtGui, QtWidgets

from mikroj.env import MACROS_PATH, PLUGIN_PATH, get_asset_file
from mikroj.helper import ImageJ
from mikroj.registries.macro import MacroRegistry

packaged = False

if packaged:
    os.environ["JAVA_HOME"] = os.path.join(os.getcwd(), "share\\jdk8")
    os.environ["PATH"] = (
        os.path.join(os.getcwd(), "share\\mvn\\bin") + os.pathsep + os.environ["PATH"]
    )


class MikroJ(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
        self.setWindowIcon(QtGui.QIcon(get_asset_file("logo.ico")))
        self.setWindowTitle("MikroJ")

        self.image_j = ImageJ()

        self.macro_registry = MacroRegistry(path=MACROS_PATH)

        self.app = ConnectedApp(
            koil=QtPedanticKoil(uvify=False, auto_connect=True, parent=self),
            fakts=Fakts(
                subapp="mikroj",
                grants=[
                    QtSelectableBeaconGrant(widget=SelectBeaconWidget(parent=self))
                ],
                assert_groups={"mikro"},
            ),
            arkitekt=Arkitekt(definition_registry=self.macro_registry),
            herre=FaktsHerre(login_on_enter=False),
        )

        self.app.arkitekt.agent.hook("before_spawn")(self.before_spawn)

        self.app.arkitekt.register()(self.show_image)

        self.app.koil.connect()

        hard_fakts = {
            "herre": {
                "client_id": "hmtwKgUO092bYBOvHngL5HVikS2q5aWbS7V1ofdU",
                "scopes": ["introspection", "can_provide"],
            }
        }

        self.magic_bar = MagicBar(self.app, dark_mode=False)

        self.setCentralWidget(self.magic_bar)

        self.macro_registry.load_macros()

    async def before_spawn(self, agent: BaseAgent, provision: Provision):
        print("Provision")

    def show_image(self, image: RepresentationFragment):
        """Show Image

        Shows the image in the viewer

        Args:
            image (RepresentationFragment): _description_
        """
        pass

    def register_macros(self):
        print("Registering Macros")


def main(**kwargs):
    app = QtWidgets.QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
    main_window = MikroJ(**kwargs)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
