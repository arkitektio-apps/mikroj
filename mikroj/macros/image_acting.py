
from ..registries.helper import get_running_helper
from ..macros.base import BaseMacro
import xarray as xr
import dask

class ImageActingMacro(BaseMacro):

    def run(self, image: xr.DataArray, helper= None, **kwargs) -> xr.DataArray:
        helper = helper or get_running_helper()
        image = image.squeeze()

        # check if we are having a dask array
        if dask.is_dask_collection(image.data):
            jimage = helper.py.to_java(image.compute())
        else:
            jimage = helper.py.to_java(image)
        # Convert the Image to Image
        if not helper.headless: helper.ui.show(image.name, jimage)
        #run the Macro
        result = super().run(**kwargs)
        print(result)
        # open synchronized image
        imp = helper.py.active_image_plus()
        array = helper.py.from_java(imp)
        if "Channel" in array.dims: array = array.rename({"Channel": "c"})
        return array