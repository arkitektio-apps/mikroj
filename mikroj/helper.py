import imagej
import scyjava
from PyQt5 import QtCore, QtGui, QtWidgets

from mikroj.registries.macro import ImageJMacroHelper
from .errors import NotStartedError


class ImageJ(QtWidgets.QWidget):
    def __init__(self, helper: ImageJMacroHelper, *args, **kwargs) -> None:
        # concatenade version plus plugins
        # build = [version] + plugins if len(plugins) > 0 else version
        # if plugins_dir:
        #   path = os.path.join(os.getcwd(),plugins_dir)
        #    scyjava.config.add_option(f'-Dplugins.dir={path}')

        super().__init__(*args, **kwargs)
        self.helper = helper
        self.settings = QtCore.QSettings("MikroJ", "App1")
        self.image_j_path = self.settings.value("image_j_path", "")
        self.auto_initialize = self.settings.value("auto_initialize", True)
        self.plugins_dir = self.settings.value("plugins_dir", "")
        self.headless = False
        self._ij = None

        self.imagej_button = QtWidgets.QPushButton("Initialize ImageJ")
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.imagej_button.clicked.connect(self.initialize)
        self.settings_button.clicked.connect(self.open_settings)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.imagej_button)
        self.layout.addWidget(self.settings_button)

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

    def initialize(self):
        if not self.image_j_path:
            self.request_imagej_dir()

        if self.plugins_dir:
            print(f"Initializing with plugins in  {self.plugins_dir}")
            scyjava.config.add_option(f"-Dplugins.dir={self.plugins_dir}")

        self.imagej_button.setDisabled(True)
        self.imagej_button.setText("Initializing...")
        self._ij = imagej.init(self.image_j_path, headless=self.headless)
        self.imagej_button.setText(f"Connected {self.headless=}")
        self.helper.set_ij_instance(self._ij)

        if not self.headless:
            self._ij.ui().showUI()

    @property
    def py(self):
        return self._ij.py

    @property
    def ui(self):
        return self._ij.ui()

    @property
    def ij(self):
        if not self._ij:
            raise NotStartedError("ImageJ is not started")
        return self._ij
