from typing import Optional, List
from pydantic import BaseModel, Field
import scyjava as sj
from mikro.api.schema import Create_roiMutation, InputVector, RoiTypeInput
import pandas as pd
import imagej
from typing import Any, Protocol

ImageJ = Any

CreateRoiArguments = Create_roiMutation.Arguments


class RoiManagerInstance(Protocol):
    def getRoisAsArray(self) -> List[Any]:
        ...


class RoiManager(Protocol):
    def getRoiManager(self) -> RoiManagerInstance:
        ...


class WindowManager(Protocol):
    def getImage(self, id: int) -> Any:
        ...


class IJProtocol(Protocol):
    WindowManager: Any
    RoiManager: RoiManager
    ResultsTable: Any


class ImageJBridge(BaseModel):
    """A small convenienve wrapper around PyImageJ to make it easier to use in mikroJ
    and to provide a more stable API (PyImageJ is still in development)

    Bridge function should NEVER call any Arkitekt API endpoints, but only give back
    primitves that can be used in Arkitekt functions. (e.g. Arguments)"""

    maximum_memory: Optional[int] = Field(default=None)
    minimum_memory: Optional[int] = Field(default=None)

    _ij: Optional[ImageJ] = None

    def set_ij_instance(self, ij: ImageJ):
        self._ij = ij

    def stop_ij_instance(self):
        if self._ij:
            self._ij.ui().dispose()
            del self._ij
            self._ij = None

    def get_imageplus_roi_id(self, id):
        imp = self.ij.WindowManager.getImage(id)
        return imp

    def active_imageplus(self):
        return self.py.active_imageplus()

    def get_rois(self) -> List[CreateRoiArguments]:
        # get ImageJ resources
        OvalRoi = sj.jimport("ij.gui.OvalRoi")
        PolygonRoi = sj.jimport("ij.gui.PolygonRoi")

        sj.jimport("ij.process.FloatPolygon")
        Overlay = sj.jimport("ij.gui.Overlay")
        Overlay()

        rm = self.ij.RoiManager.getRoiManager()
        rois = rm.getRoisAsArray()

        arguments = []

        for roi in rois:
            image_plus = self.ij.WindowManager.getImage(roi.getImageID())
            ds = self.py.to_dataset(
                image_plus
            )  # conversion of legacy ImagePlus to Dataset

            id = ds.getProperties().get("representation_id")
            if id:
                if isinstance(roi, OvalRoi):
                    pass
                if isinstance(roi, PolygonRoi):
                    t = roi.getFloatPolygon()
                    arguments.append(
                        CreateRoiArguments(
                            representation=id,
                            type=RoiTypeInput.POLYGON,
                            vectors=[
                                InputVector(x=x, y=y)
                                for x, y in zip(t.xpoints, t.ypoints)
                            ],
                        )
                    )

        return arguments

    def run_macro(self, macro: str, args: dict):
        """Runs a macro with the given arguments

        Parameters
        ----------
        macro : str
            The macro code
        args : dict
            The arguments

        Returns
        -------
        _type_
            _description_
        """

        exec_info = self.py.run_macro(macro, args)
        print(exec_info)

        return exec_info

    def run_plugin_v1(self, plugin_name: str, args: dict):
        """Runs a plugin with the given arguments

        Parameters
        ----------
        plugin_name : str
            The plugin name
        args : dict
            The arguments

        Returns
        -------
        _type_
            _description_
        """
        return self.py.run_plugin(plugin_name, args)

    def get_results_as_df(self) -> pd.DataFrame:
        """Returns the results table as a pandas DataFrame"""
        # get ImageJ resources
        Table = sj.jimport("org.scijava.table.Table")
        results = self.ij.ResultsTable.getResultsTable()
        table = self.ij.convert().convert(results, Table)
        measurements = self.py.from_java(table)

        return measurements

    def get_results_as_sjtable(self):
        """Returns the results table as a scijava Table"""
        Table = sj.jimport("org.scijava.table.Table")
        results = self.ij.ResultsTable.getResultsTable()
        return self.ij.convert().convert(results, Table)

    @property
    def active_rois(self):
        return self.ij.roiManager().getRoisAsArray()

    @property
    def py(self) -> imagej.ImageJPython:
        assert self._ij is not None, "No ImageJ instance found"
        return self._ij.py

    @property
    def ij(self) -> IJProtocol:
        assert self._ij is not None, "No ImageJ instance found"
        return self._ij

    @property
    def ui(self):
        assert self._ij is not None, "No ImageJ instance found"
        return self._ij.ui()

    class Config:
        arbitary_types_allowed = True
        underscore_attrs_are_private = True
        copy_on_model_validation = False
