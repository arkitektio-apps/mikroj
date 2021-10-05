import sys
from PyQt5 import QtWidgets
import imagej

class MikroJ(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._ij = imagej.init("sc.fiji:fiji:2.1.0", headless=False)

        self.init_ui()

    def init_ui(self):
        self._ij.ui().showUI()
        self.setWindowTitle('MikroJ - fucking ImageJ')
        self.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MikroJ()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()