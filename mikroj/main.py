import os
import sys
from arkitekt.qt.magic_bar import MagicBar
from mikroj.env import get_asset_file
import imagej
from qtpy.QtWidgets import QMessageBox
from qtpy import QtWidgets, QtGui, QtCore
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
from mikro.api.schema import from_xarray, TableFragment, from_df
from rekuest.widgets import ParagraphWidget
from rekuest.structures.default import get_default_structure_registry
from mikroj import constants, structures
from typing import List, Optional
from mikroj.bridge import ImageJBridge
import scyjava as sj
from mikroj.language.transpile import TranspileRegistry
from mikroj.extension import MacroExtension



identifier = "github.io.jhnnsrs.mikroj"
version = "v0.0.1"


structure_registry = get_default_structure_registry()
structure_registry.register_as_structure(
    structures.ImageJPlus, constants.IMAGEJ_PLUS_IDENTIFIER
)


class MikroJ(QtWidgets.QWidget):
    bridge: Optional[ImageJBridge] = None

    def __init__(self, *args, auto_init=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.setWindowIcon(QtGui.QIcon(get_asset_file("logo.ico")))
        self.setWindowTitle("MikroJ")

        self.settings = QtCore.QSettings("MikroJ", "ss")
        self.image_j_path = self.settings.value("image_j_path", "")
        self.auto_initialize = auto_init  if auto_init else self.settings.value("auto_initialize", True)
        self.plugins_dir = self.settings.value("plugins_dir", "")

        self.bridge = ImageJBridge()
        self.transpile_registry = TranspileRegistry()

        self.app = publicscheduleqt(
            identifier=identifier,
            version=version,
            log_level="INFO",
            parent=self,
        )

        self.app.rekuest.register_extension(
            "macro",
            MacroExtension(
                bridge=self.bridge,
                structure_registry=structure_registry,
                transpile_registry=self.transpile_registry,
            ),
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
            self.get_results_as_table,
            structure_registry=structure_registry,
        )
        self.app.rekuest.register(
            self.analyze_particles,
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

        self.imagej_button = QtWidgets.QPushButton("Initialize ImageJ")
        self.settings_button = QtWidgets.QPushButton("Change ImageJ")
        self.imagej_button.clicked.connect(self.initialize)
        self.settings_button.clicked.connect(self.open_settings)

        self.done_yet_widget = None

        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.addWidget(self.imagej_button)
        self.vlayout.addWidget(self.settings_button)
        self.vlayout.addWidget(self.magic_bar)

        self.setLayout(self.vlayout)
        self.magic_bar.magicb.setDisabled(True)
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

    def ask_if_done(self, qtfuture, message: str):
        """Ask if user is done"""
        self.done_yet_widget = DoneYetWidget(qtfuture, message)
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
            image.data.compute(), image.name, self.bridge
        )
        image_plus.set_active()
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
        data = image.to_xarray()
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
        self.bridge.run_macro(macro, {})
        imageplus = self.bridge.active_imageplus()
        return structures.ImageJPlus(imageplus, image.name, self.bridge)

    def analyze_particles(
        self, image: RepresentationFragment
    ) -> Tuple[TableFragment, RepresentationFragment]:
        """Analyze Particles

        Analyzes particles in an image

        Parameters
        ----------
        image : RepresentationFragment
            The image
        """
        image_plus, name = self.load_into_imagej(image)
        macro = """
        run("8-bit");
        setAutoThreshold("Default dark");
        run("Analyze Particles...", "size=0-Infinity circularity=0.00-1.00 show=[Count Masks]  display exclude clear add");
        """
        after_image = self.run_image_to_image_macro(image_plus, macro)
        results = self.get_results_as_table(f"Analyzd Particles of {name}", [image])
        uploaded = from_xarray(
            after_image.to_xarray(),
            name="Particles of " + name,
            origins=[image],
            variety=RepresentationVarietyInput.MASK,
        )
        image_plus.close()
        after_image.close()
        return results, uploaded

    def get_labels(self, image: structures.ImageJPlus):
        ImagePlus = sj.jimport("ij.ImagePlus")
        mask = ImagePlus("cells-mask", image.value.createThresholdMask())
        x = structures.ImageJPlus(mask, "cells-mask", self.bridge)
        x.set_active()
        overlay = image.value.getOverlay()
        print(mask, overlay)
        return image.get_as_label()

    def get_results_as_table(
        self,
        name: Optional[str],
        image_origins: Optional[List[RepresentationFragment]],
    ) -> TableFragment:
        """Get Results Table

        Gets the results table and converts it to a TableFragment

        """
        measurements = self.bridge.get_results_as_df()

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

        sj.jimport("ij.process.FloatPolygon")
        Overlay = sj.jimport("ij.gui.Overlay")
        Overlay()

        rm = self.bridge._ij.RoiManager.getRoiManager()
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
            path = (
                os.getcwd()
            )  # This is a hack until https://github.com/imagej/pyimagej/issues/150
            self._ij = imagej.init(self.image_j_path, mode="interactive")
            os.chdir(path)  ## 
            self.imagej_button.setText("ImageJ Initialized")
            self.magic_bar.magicb.setDisabled(False)

            self.vlayout.update()

            self.bridge.set_ij_instance(self._ij)
            self._ij.ui().showUI()
            self.magic_bar.magicb.setDisabled(False)

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
        except Exception:
            traceback.print_exc()


def main(run_packaged=False, **kwargs):

    if run_packaged:
        os.environ["JAVA_HOME"] = os.path.join(os.getcwd(), "share\\jdk")
        os.environ["PATH"] = (
            os.path.join(os.getcwd(), "share\\mvn\\bin") + os.pathsep + os.environ["PATH"]
        )



    qtapp = QtWidgets.QApplication(sys.argv)

    main_window = MikroJ(**kwargs)
    main_window.show()
    sys.exit(qtapp.exec_())


if __name__ == "__main__":
    main()
