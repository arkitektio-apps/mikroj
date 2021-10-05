import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
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


class MikroJ(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.helper = ImageJHelper()
        self.layout = QtWidgets.QHBoxLayout()
        self.start_button = QtWidgets.QPushButton("Show")
        self.start_button.clicked.connect(self.show_image)
        self.setCentralWidget(self.start_button)
        self.init_ui()

    def show_image(self):
        array = xr.DataArray(np.zeros((3,1024,1024)), dims=list("cxy"), name="Nanana")
        self.helper.show_xarray(array)
        

    def init_ui(self):
        self.setWindowTitle('MikroJ - fucking ImageJ')
        self.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MikroJ()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()