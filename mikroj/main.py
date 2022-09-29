import logging
import os
import sys
from arkitekt.apps.rekuest import ArkitektRekuest
from arkitekt.qt.magic_bar import MagicBar
from fakts.discovery.static import StaticDiscovery
from fakts.fakts import Fakts
from fakts.grants.meta.failsafe import FailsafeGrant
from fakts.grants.remote.claim import ClaimGrant
from fakts.grants.remote.public_redirect_grant import PublicRedirectGrant
from koil.composition.qt import QtPedanticKoil
from arkitekt.apps.connected import ConnectedApp
from PyQt5 import QtCore, QtGui, QtWidgets
from .actors.base import jtranspile, ptranspile
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
            rekuest=ArkitektRekuest(definition_registry=self.macro_registry),
        )

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

    def run_macro(self, macro, **kwargs):

        transpiled_args = {
            key: jtranspile(kwarg, self.helper) for key, kwarg in kwargs.items()
        }

        if self.macro.setactivein:
            image = transpiled_args.pop(self.provision.template.node.args[0].key)
            self.helper.ui.show(
                kwargs[self.provision.template.node.args[0].key].name, image
            )
        macro_output = self.helper.py.run_macro(self.macro.code, {**transpiled_args})

        logging.debug(f"{macro_output}")
        imagej_returns = []

        if self.macro.takeactiveout:
            imagej_returns.append(self.helper.py.active_image_plus())

        for index, re in enumerate(self.provision.template.node.returns):
            if index == 0 and self.macro.takeactiveout:
                continue  # we already put the image out
            imagej_returns.append(macro_output.getOutput(re.key))

        transpiled_returns = [
            ptranspile(value, kwargs, self.helper, self.macro, self.provision)
            for value in imagej_returns
        ]

        if len(transpiled_returns) == 0:
            return None
        if len(transpiled_returns) == 1:
            return transpiled_returns[0]
        else:
            return transpiled_returns

    def initialize(self):
        if not self.image_j_path:
            self.magic_bar.magicb.setDisabled(True)
            self.request_imagej_dir()

        if self.plugins_dir:
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
