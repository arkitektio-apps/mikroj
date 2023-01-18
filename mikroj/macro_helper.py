from typing import Optional, List
from pydantic import BaseModel, Field
import scyjava as sj
from mikro.api.schema import Create_roiMutation, InputVector, RoiTypeInput
import pandas as pd

CreateRoiArguments = Create_roiMutation.Arguments

class ImageJMacroHelper(BaseModel):
    maximum_memory: Optional[int] = Field(default=None)
    minimum_memory: Optional[int] = Field(default=None)

    _ij = None

    def set_ij_instance(self, ij):
        self._ij = ij

    def get_imageplus_roi_id(self, id):
        imp = self._ij.WindowManager.getImage(id)
        return imp

    def get_rois(self) -> List[CreateRoiArguments]:
        # get ImageJ resources
        OvalRoi = sj.jimport('ij.gui.OvalRoi')
        PolygonRoi = sj.jimport('ij.gui.PolygonRoi')

        FloatPolygon = sj.jimport('ij.process.FloatPolygon')
        Overlay = sj.jimport('ij.gui.Overlay')
        ov = Overlay()


        rm = self._ij.RoiManager.getRoiManager()
        rois = rm.getRoisAsArray()

        arguments = []

        for roi in rois:
            image_plus = self._ij.WindowManager.getImage(roi.getImageID())
            ds = self._ij.py.to_dataset(image_plus) # conversion of legacy ImagePlus to Dataset

            id = ds.getProperties().get("representation_id")
            if id:
                if isinstance(roi, OvalRoi):
                    print(roi)
                if isinstance(roi, PolygonRoi):
                    t = roi.getFloatPolygon()
                    arguments.append(CreateRoiArguments(representation=id, type=RoiTypeInput.POLYGON, vectors=[InputVector(x=x, y=y) for x, y in zip(t.xpoints, t.ypoints)]))

        return arguments

    def get_results(self) -> pd.DataFrame:
        # get ImageJ resources
        Table = sj.jimport('org.scijava.table.Table')
        results = self._ij.ResultsTable.getResultsTable()
        print(results.getProperties())
        table = self._ij.convert().convert(results, Table)
        measurements = self._ij.py.from_java(table)
        print(measurements)

        return measurements

    def get_results_table(self):
        Table = sj.jimport('org.scijava.table.Table')
        results = self._ij.ResultsTable.getResultsTable()
        return self._ij.convert().convert(results, Table)


    @property
    def active_rois(self):

        return self._ij.roiManager().getRoisAsArray()

    @property
    def py(self):
        return self._ij.py

    @property
    def ui(self):
        return self._ij.ui()

    class Config:
        arbitary_types_allowed = True
        underscore_attrs_are_private = True
