import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, Qt
import imagej
import os
import logging
logging.basicConfig(level=logging.DEBUG)
import scyjava
import numpy as np
from mikroj.helper import ImageJHelper
import xarray as xr

#os.environ['JAVA_HOME'] = os.path.join(os.getcwd(), 'share\\jdk8')
os.environ['PATH'] = os.path.join(os.getcwd(), 'share\\mvn\\bin') + os.pathsep + os.environ['PATH']


class ImageJRunner(QObject):
    init_signal = QtCore.pyqtSignal(str)

    def run_it(self):
        # I'm guessing this is an infinite while loop that monitors files
        self.helper = ImageJHelper()
        self.init_signal.emit('yes')



class MikroJ(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))

        
        self.runner = ImageJRunner()
        self.thread = QtCore.QThread(self)
        self.runner.init_signal.connect(self.imagej_done)
        self.layout = QtWidgets.QHBoxLayout()
        self.runner.moveToThread(self.thread)
        self.thread.started.connect(self.runner.run_it)
        self.thread.start()
        self.start_button = QtWidgets.QPushButton("Loading")
        self.start_button.setDisabled(True)
        self.start_button.clicked.connect(self.show_image)
        self.setCentralWidget(self.start_button)
        self.init_ui()

    def show_image(self):
        array = xr.DataArray(np.zeros((3,1024,1024)), dims=list("cxy"), name="Nanana")
        self.runner.helper.show_xarray(array)
        
    def imagej_done(self, str):
        self.start_button.setDisabled(False)
        self.start_button.setText("Assign")

    def init_ui(self):
        self.setWindowTitle('MikroJ - fucking ImageJ')
        self.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
    main_window = MikroJ()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()