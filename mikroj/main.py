from abc import abstractmethod
import abc
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QRect, Qt, pyqtSignal
import os
from pydantic.class_validators import extract_root_validators
from arkitekt.actors.registry import register
from arkitekt.qt.utils import register_ui
from herre.qt import QtHerre
from pydantic.main import BaseModel
from arkitekt.messages.base import T
from fakts.grants.qt.qtbeacon import QtSelectableBeaconGrant
from fakts.grants.qt.qtyamlgrant import QtYamlGrant
from fakts.grants.yaml import YamlGrant
from fakts.qt import QtFakts
from mikro import Representation
from mikroj.agent import MikroJAgent
from mikroj.env import MACROS_PATH, PLUGIN_PATH, get_asset_file
from mikroj.helper import ImageJHelper
from arkitekt.qt.agent import QtAgent
from mikro.widgets import MY_TOP_REPRESENTATIONS
from arkitekt.qt.widgets.provisions import ProvisionsWidget
from arkitekt.qt.widgets.templates import TemplatesWidget
from arkitekt.qt.widgets.magic_bar import MagicBar
import os

from mikroj.structures.imageplus import ImagePlus


packaged = False

if packaged:
    os.environ["JAVA_HOME"] = os.path.join(os.getcwd(), "share\\jdk8")
    os.environ["PATH"] = (
        os.path.join(os.getcwd(), "share\\mvn\\bin") + os.pathsep + os.environ["PATH"]
    )


helper = ImageJHelper()


class FormWrapped(QtWidgets.QWidget):
    def __init__(self, widget, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QtWidgets.QHBoxLayout()
        self.formGroupBox = QtWidgets.QGroupBox(title)
        qlayout = QtWidgets.QFormLayout()
        qlayout.addRow(widget)
        self.formGroupBox.setLayout(qlayout)
        self.layout.addWidget(self.formGroupBox)
        self.setLayout(self.layout)


class ArkitektWidget(QtWidgets.QWidget):
    def __init__(self, helper, *args, config_path=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Different Grants

        self.beacon_grant = QtSelectableBeaconGrant()
        self.fakts = QtFakts(
            grants=[self.beacon_grant],
            subapp="mikroj",
            hard_fakts={
                "herre": {
                    "client_id": "hmtwKgUO092bYBOvHngL5HVikS2q5aWbS7V1ofdU",
                    "scopes": ["introspection", "can_provide"],
                }
            },
        )
        self.herre = QtHerre()
        self.agent = MikroJAgent(helper, self)

        self.magic_bar = MagicBar(self.fakts, self.herre, self.agent)
        self.agent.load_macros(MACROS_PATH)

        self.layout = QtWidgets.QVBoxLayout()

        self.provisions_widget = FormWrapped(ProvisionsWidget(self.agent), "Provisions")
        self.templates_widget = FormWrapped(TemplatesWidget(self.agent), "Templates")

        self.layout.addWidget(self.magic_bar)
        self.layout.addWidget(self.provisions_widget)
        self.layout.addWidget(self.templates_widget)
        self.setLayout(self.layout)


def show_image(rep: Representation):
    """Shows an Image

    Shows a Representation on Imagej

    Args:
        rep (Representation): A Beautiful Little Image to display
    """


@register(interfaces=["bridge"])
def bridge(rep: Representation) -> ImagePlus:
    """Bridges a thing to a thang

    Bridges an Representation to an In memory Fiji Image

    Args:
        rep (Representation): [description]

    Returns:
        ImagePlus: [description]
    """
    print(rep)
    array = rep.data.compute()
    print(array)

    plus = ImagePlus(array)
    print(plus)
    return plus


class MikroJ(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        # self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
        self.setWindowIcon(QtGui.QIcon(get_asset_file("logo.ico")))

        self.arkitektWidget = ArkitektWidget(helper, **kwargs)

        self.agent = self.arkitektWidget.agent

        self.showActor = self.agent.register_ui(
            show_image, widgets={"rep": MY_TOP_REPRESENTATIONS}
        )

        self.showActor.signals.assign.wire(self.show_image_assign)

        self.layout = QtWidgets.QHBoxLayout()
        self.setCentralWidget(self.arkitektWidget)
        self.init_ui()

    def show_image_assign(self, res, args, kwargs):
        helper.displayRep(args[0])
        self.showActor.signals.assign.resolve(res, None)

    def init_ui(self):
        self.setWindowTitle("MikroJ")
        self.show()


def main(**kwargs):
    app = QtWidgets.QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
    main_window = MikroJ(**kwargs)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
