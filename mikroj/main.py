import os
import sys
from arkitekt.qt.magic_bar import MagicBar
from PyQt5 import QtCore, QtGui, QtWidgets
from mikroj.env import get_asset_file
import imagej
from PyQt5 import QtCore, QtGui, QtWidgets
from fakts.discovery.qt.selectable_beacon import (
    SelectBeaconWidget,
)
from herre.grants.qt.login_screen import LoginWidget
from qtpy.QtWidgets import QMessageBox
from rekuest.qt.builders import qtwithfutureactifier, qtinloopactifier
from mikroj.widgets.done_yet import DoneYetWidget
from arkitekt.builders import publicscheduleqt
from mikro.api.schema import (
    RepresentationFragment,
    RepresentationVarietyInput,
    ROIFragment,
    create_roi,
    RoiTypeInput,
    InputVector,
)
import traceback
from typing import Tuple
from typing import Optional
from mikro.api.schema import from_xarray, TableFragment, from_df
from rekuest.widgets import ParagraphWidget
from rekuest.structures.default import get_default_structure_registry
from rekuest.api.schema import TemplateFragment, create_template
from mikroj import constants, structures
from typing import List, Optional
from mikroj.macro_helper import ImageJMacroHelper
import scyjava as sj
from mikroj.language.transpile import TranspileRegistry
from mikroj.language.parse import parse_macro
from mikroj.language.define import define_macro
from mikroj.extension import MacroExtension

packaged = False
identifier = "github.io.jhnnsrs.mikroj"
version = "v0.0.1"

if packaged:
    os.environ["JAVA_HOME"] = os.path.join(os.getcwd(), "share\\jdk")
    os.environ["PATH"] = (
        os.path.join(os.getcwd(), "share\\mvn\\bin") + os.pathsep + os.environ["PATH"]
    )


structure_registry = get_default_structure_registry()
structure_registry.register_as_structure(
    structures.ImageJPlus, constants.IMAGEJ_PLUS_IDENTIFIER
)


class MikroJ(QtWidgets.QWidget):
    helper: Optional[ImageJMacroHelper] = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # self.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
        self.setWindowIcon(QtGui.QIcon(get_asset_file("logo.ico")))
        self.setWindowTitle("MikroJ")

        self.settings = QtCore.QSettings("MikroJ", "ss")
        self.image_j_path = self.settings.value("image_j_path", "")
        self.auto_initialize = self.settings.value("auto_initialize", True)
        self.plugins_dir = self.settings.value("plugins_dir", "")
        self.helper = ImageJMacroHelper()
        self.transpile_registry = TranspileRegistry()

        self.app = publicscheduleqt(
            identifier=identifier,
            version=version,
            log_level="INFO",
            parent=self,
        )

        self.app.rekuest.agent.extensions["macro"] = MacroExtension(
            helper=self.helper,
            structure_registry=structure_registry,
            transiple_registry=self.transpile_registry,
        )

        self.magic_bar = MagicBar(
            self.app, on_error=self.show_exception, dark_mode=False
        )

        self.app.rekuest.register(
            self.ask_if_done,
            actifier=qtwithfutureactifier,
            name="Ask if done",
            description="Ask if the user is done",
            structure_registry=structure_registry,
        )

        self.app.rekuest.register(
            self.load_into_imagej,
            structure_registry=structure_registry,
        )
        self.app.rekuest.register(
            self.get_results_table,
            structure_registry=structure_registry,
        )
        self.app.rekuest.register(
            self.run_image_to_image_macro,
            actifier=qtinloopactifier,
            widgets={"macro": ParagraphWidget()},
            structure_registry=structure_registry,
        )
        self.app.rekuest.register(
            self.get_active_rois,
            actifier=qtinloopactifier,
            structure_registry=structure_registry,
        )

        self.app.rekuest.register(
            self.retrieve_from_image,
            actifier=qtinloopactifier,
            structure_registry=structure_registry,
        )

        self.headless = False
        self._ij: imagej = None

        self.imagej_button = QtWidgets.QPushButton("Initialize ImageJ")
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.imagej_button.clicked.connect(self.initialize)
        self.settings_button.clicked.connect(self.open_settings)

        self.done_yet_widget = None

        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.addWidget(self.imagej_button)
        self.vlayout.addWidget(self.settings_button)
        self.vlayout.addWidget(self.magic_bar)

        self.setLayout(self.vlayout)
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
        self.request_imagej_dir()
        pass

    def get_rois(self):
        self.helper.get_rois()

    def get_results(self):
        self.helper.get_results()

    def ask_if_done(self, future, message: str):
        self.done_yet_widget = DoneYetWidget(future, message)
        self.done_yet_widget.show()

    def load_into_imagej(
        self,
        image: RepresentationFragment,
    ) -> Tuple[structures.ImageJPlus, str]:
        """Load into Imagej

        Loads the image into imagej

        Parameters
        ----------
        a : RepresentationFragment
            The image

        Returns
        -------
        image : ImageJPlus
            The returned image

        name : str
            The original name
        """
        image_plus = structures.ImageJPlus.from_xarray(
            image.data.compute(), image.name, self.helper
        )
        image_plus.set_active(self.helper)
        return (
            image_plus,
            image.name,
        )

    def retrieve_from_image(
        self,
        image: structures.ImageJPlus,
        name: str,
        origin: Optional[RepresentationFragment] = None,
        variety: RepresentationVarietyInput = RepresentationVarietyInput.VOXEL,
    ) -> RepresentationFragment:
        """Retrieve from imageJ

        Parameters
        ----------
        image : ImageJPlus
            The original Image
        name : str
            The name of the image to be created
        origin : Optional[RepresentationFragment], optional
           The original image that this immage was created from
        variety: RepresentationVarietyInput, optional
            The variety of the image (default: VOXEL)

        Returns
        -------
        image: RepresentationFragment
            The new image
        """
        data = image.to_xarray(self.helper)
        return from_xarray(
            data,
            name=name or image.name,
            origins=[origin] if origin else None,
            variety=variety,
        )

    def run_image_to_image_macro(
        self, image: structures.ImageJPlus, macro: str
    ) -> structures.ImageJPlus:
        """Run Image Macro

        Runs an image macro as provided as a str on an Image

        Parameters
        ----------
        image : ImageJPlus
            The image
        macro : str
            The macro code

        Returns
        -------
        ImageJPlus
            The newly active image
        """
        image.set_active()
        execution_info = self.helper.py.run_macro(macro, {})
        imageplus = self.helper.py.active_imageplus()
        return structures.ImageJPlus(imageplus, image.name)

    def get_results_table(
        self,
        name: Optional[str],
        image_origins: Optional[List[RepresentationFragment]],
    ) -> TableFragment:
        """Get Results Table

        Gets the results table and converts it to a TableFragment

        """
        Table = sj.jimport("org.scijava.table.Table")
        results = self.helper._ij.ResultsTable.getResultsTable()
        table = self.helper._ij.convert().convert(results, Table)
        measurements = self.helper._ij.py.from_java(table)

        return from_df(measurements, name=name or "Results", rep_origins=image_origins)

    def get_active_rois(
        self, imageplus: structures.ImageJPlus, image: RepresentationFragment
    ) -> List[ROIFragment]:
        """Get Active ROIs

        Gets the active ROIs

        Returns
        -------
        List[ROIFragment]
            The active ROIs
        """

        OvalRoi = sj.jimport("ij.gui.OvalRoi")
        PolygonRoi = sj.jimport("ij.gui.PolygonRoi")

        FloatPolygon = sj.jimport("ij.process.FloatPolygon")
        Overlay = sj.jimport("ij.gui.Overlay")
        ov = Overlay()

        rm = self.helper._ij.RoiManager.getRoiManager()
        rois = rm.getRoisAsArray()

        arguments = []

        for roi in rois:
            on_image = roi.getImageID()

            if on_image == imageplus.get_image_id():
                if isinstance(roi, OvalRoi):
                    pass
                if isinstance(roi, PolygonRoi):
                    t = roi.getFloatPolygon()
                    arguments.append(
                        create_roi(
                            representation=image.id,
                            type=RoiTypeInput.POLYGON,
                            vectors=[
                                InputVector(x=x, y=y)
                                for x, y in zip(t.xpoints, t.ypoints)
                            ],
                        )
                    )

        return arguments

    def initialize(self):
        if not self.image_j_path:
            self.magic_bar.magicb.setDisabled(True)
            self.request_imagej_dir()

        if self.plugins_dir:
            # scyjava.config.add_option(f"-Dplugins.dir={self.plugins_dir}")
            pass

        try:
            self.imagej_button.setDisabled(True)
            self.imagej_button.setText("Initializing...")
            path = os.getcwd()
            self._ij = imagej.init(self.image_j_path, mode="interactive")
            os.chdir(path)
            self.imagej_button.setText("ImageJ Initialized")
            self.magic_bar.magicb.setDisabled(False)

            self.vlayout.update()

            self.helper.set_ij_instance(self._ij)

            if not self.headless:
                self._ij.ui().showUI()
        except Exception as e:
            self.image_j_path = None
            self.imagej_button.setText("ImageJ Failed to Initialize")
            self.magic_bar.magicb.setDisabled(True)
            self.imagej_button.setDisabled(False)
            self.show_exception(e)

    def show_exception(self, exception: Exception):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(
            str(exception)
            + "\n"
            + "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )
        )
        msg.setWindowTitle("Error")
        msg.exec_()

        try:
            raise exception
        except Exception as e:
            traceback.print_exc()

    def add_testing_ui(self):
        self.get_rois_button = QtWidgets.QPushButton("Get ROIs")
        self.vlayout.addWidget(self.get_rois_button)

        self.get_results_button = QtWidgets.QPushButton("Get Results")
        self.vlayout.addWidget(self.get_results_button)

        self.get_rois_button.clicked.connect(self.get_rois)
        self.get_results_button.clicked.connect(self.get_results)


def main(**kwargs):
    app = QtWidgets.QApplication(sys.argv)

    # app.setWindowIcon(QtGui.QIcon(os.path.join(os.getcwd(), 'share\\assets\\icon.png')))
    main_window = MikroJ(**kwargs)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
