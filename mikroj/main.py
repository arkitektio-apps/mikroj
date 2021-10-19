from abc import abstractmethod
import abc
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QRect, Qt, pyqtSignal
import os
from pydantic.class_validators import extract_root_validators
from herre.qt import QtHerre
from pydantic.main import BaseModel
from arkitekt.messages.base import T
from fakts.grants.qtbeacon import QtSelectableBeaconGrant
from fakts.grants.qtyamlgrant import QtYamlGrant
from fakts.grants.yaml import YamlGrant
from fakts.qt import QtFakts
from mikro import Representation
from mikroj.agent import MikroJAgent
from mikroj.env import PLUGIN_PATH
from mikroj.helper import ImageJHelper
from arkitekt.agents.qt import QtAgent
from mikro.widgets import MY_TOP_REPRESENTATIONS
from arkitekt.qt.widgets.provisions import ProvisionsWidget
from arkitekt.qt.widgets.templates import TemplatesWidget
from arkitekt.qt.widgets.magic_bar import MagicBar
import os


packaged = False

if packaged:
    os.environ['JAVA_HOME'] = os.path.join(os.getcwd(), 'share\\jdk8')
    os.environ['PATH'] = os.path.join(os.getcwd(), 'share\\mvn\\bin') + os.pathsep + os.environ['PATH']


class ImageJRunner(QObject):
    init_signal = QtCore.pyqtSignal(str)


    def __init__(self, *args, **kwargs) -> None:
        super().__init__( *args, **kwargs)
        self.helper = None

    def run_it(self):
        # I'm guessing this is an infinite while loop that monitors files
        self.helper = ImageJHelper()
        self.init_signal.emit('yes')





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

        self.file_grant = QtYamlGrant("querk.yaml")
        self.beacon_grant = QtSelectableBeaconGrant()
        self.fakts = QtFakts(grants=[self.file_grant, self.beacon_grant], save_conf="querk.yaml")
        self.herre = QtHerre()
        self.agent = MikroJAgent(helper, self)

        self.magic_bar = MagicBar(self.fakts, self.herre, self.agent)
        self.agent.load_macros(PLUGIN_PATH)


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




class MikroJ(QtWidgets.QMainWindow):
    def __init__(self, **kwargs):
        super().__init__()
        #self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))


        self.runner = ImageJRunner()
        self.arkitektWidget = ArkitektWidget(self.runner.helper, **kwargs)

        self.agent = self.arkitektWidget.agent

        self.showActor = self.agent.register(show_image, widgets={"rep": MY_TOP_REPRESENTATIONS})
        self.showActor.signals.assign.call.connect(self.show_image_assign)

        self.thread = QtCore.QThread(self)
        self.runner.init_signal.connect(self.imagej_done)
        self.layout = QtWidgets.QHBoxLayout()
        self.runner.moveToThread(self.thread)
        self.thread.started.connect(self.runner.run_it)
        self.thread.start()
        self.arkitektWidget.magic_bar.magicb.setDisabled(True)
        self.setCentralWidget(self.arkitektWidget)
        self.init_ui() 



    def show_image_assign(self, res, args, kwargs):
        self.runner.helper.displayRep(args[0])
        self.showActor.signals.assign.resolve.emit(res, None)
        
    def imagej_done(self, str):
        #self.arkitektWidget.start_button.setDisabled(False)
        #self.arkitektWidget.start_button.setText("Assign")
        self.arkitektWidget.magic_bar.magicb.setDisabled(False)

    def init_ui(self):
        self.setWindowTitle('MikroJ')
        self.show()

def main(**kwargs):
    app = QtWidgets.QApplication(sys.argv)
    #app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
    main_window = MikroJ(**kwargs)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()