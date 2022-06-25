import abc
import os
import sys
from arkitekt.agents.base import BaseAgent
from arkitekt.compositions.base import Arkitekt
from arkitekt.messages import Provision
from arkitekt.qt.magic_bar import MagicBar
from fakts.discovery.static import StaticDiscovery
from fakts.fakts import Fakts
from fakts.grants.meta.failsafe import FailsafeGrant
from fakts.grants.remote.claim import ClaimGrant
from fakts.grants.remote.public_redirect_grant import PublicRedirectGrant
from herre.fakts.herre import FaktsHerre
from koil.composition.qt import QtPedanticKoil
from mikro.api.schema import RepresentationFragment
from mikro.arkitekt import ConnectedApp
from PyQt5 import QtCore, QtGui, QtWidgets
from fakts.grants.remote.redirect_grant import RedirectGrant
from mikroj.env import MACROS_PATH, PLUGIN_PATH, get_asset_file
from mikroj.helper import ImageJ
from mikroj.registries.macro import ImageJMacroHelper, MacroRegistry
import imagej
import scyjava
from PyQt5 import QtCore, QtGui, QtWidgets

from mikroj.registries.macro import ImageJMacroHelper
from .errors import NotStartedError


packaged = False

if packaged:
    os.environ["JAVA_HOME"] = os.path.join(os.getcwd(), "share\\jdk8")
    os.environ["PATH"] = (
        os.path.join(os.getcwd(), "share\\mvn\\bin") + os.pathsep + os.environ["PATH"]
    )


class MikroJ(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
        self.setWindowIcon(QtGui.QIcon(get_asset_file("logo.ico")))
        self.setWindowTitle("MikroJ")

        self.settings = QtCore.QSettings("MikroJ", "App1")
        self.image_j_path = self.settings.value("image_j_path", "")
        self.auto_initialize = self.settings.value("auto_initialize", True)
        self.plugins_dir = self.settings.value("plugins_dir", "")

        self.macro_registry = MacroRegistry(path=MACROS_PATH)

        self.app = ConnectedApp(
            koil=QtPedanticKoil(uvify=False, parent=self),
            fakts=Fakts(
                subapp="mikroj",
                grant=FailsafeGrant(
                    grants=[
                        ClaimGrant(
                            client_id="DSNwVKbSmvKuIUln36FmpWNVE2KrbS2oRX0ke8PJ",
                            client_secret="Gp3VldiWUmHgKkIxZjL2aEjVmNwnSyIGHWbQJo6bWMDoIUlBqvUyoGWUWAe6jI3KRXDOsD13gkYVCZR0po1BLFO9QT4lktKODHDs0GyyJEzmIjkpEOItfdCC4zIa3Qzu",
                            discovery=StaticDiscovery(
                                base_url="http://localhost:8019/f/"
                            ),
                            graph="localhost",
                        ),
                        PublicRedirectGrant(name="MikroJ", scopes=["openid"]),
                    ],
                ),
                assert_groups={"mikro"},
            ),
            arkitekt=Arkitekt(definition_registry=self.macro_registry),
        )

        self.app.arkitekt.agent.hook("before_spawn")(self.before_spawn)

        self.app.enter()

        self.magic_bar = MagicBar(self.app, dark_mode=False)

        self.macro_registry.load_macros()

        self.headless = False
        self._ij = None

        self.imagej_button = QtWidgets.QPushButton("Initialize ImageJ")
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.imagej_button.clicked.connect(self.initialize)
        self.settings_button.clicked.connect(self.open_settings)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.imagej_button)
        self.layout.addWidget(self.settings_button)
        self.layout.addWidget(self.magic_bar)

        self.setLayout(self.layout)
        if self.image_j_path and self.auto_initialize:
            self.initialize()

    async def before_spawn(self, agent: BaseAgent, provision: Provision):
        print("Provision")

    def request_imagej_dir(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self, caption="Select ImageJ directory"
        )
        if dir:
            self.image_j_path = dir
            self.settings.setValue("image_j_path", dir)
        else:
            self.image_j_path = ""
            self.settings.setValue("image_j_path", "")

    def open_settings(self):
        pass

    def initialize(self):
        if not self.image_j_path:
            self.magic_bar.magicb.setDisabled(True)
            self.request_imagej_dir()

        if self.plugins_dir:
            print(f"Initializing with plugins in  {self.plugins_dir}")
            scyjava.config.add_option(f"-Dplugins.dir={self.plugins_dir}")

        self.imagej_button.setDisabled(True)
        self.imagej_button.setDisabled(True)
        self.imagej_button.setText("Initializing...")
        self._ij = imagej.init(self.image_j_path, headless=self.headless)
        self.magic_bar.magicb.setDisabled(False)
        self.macro_registry.helper.set_ij_instance(self._ij)

        if not self.headless:
            self._ij.ui().showUI()


def main(**kwargs):
    app = QtWidgets.QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
    main_window = MikroJ(**kwargs)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
