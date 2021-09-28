
from typing import Any
from ..macros.image_acting import ImageActingMacro
import xarray as xr
import dask

class FilterMacro(ImageActingMacro):

    def __call__(self, image: xr.DataArray, **kwargs: Any) -> xr.DataArray:
        return super().run(image, **kwargs)