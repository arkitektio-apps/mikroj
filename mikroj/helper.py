from mikro.schema import Representation
from mikroj.registries.helper import BaseImageJHelper, set_running_helper
import dask
import xarray as xr


class ImageJHelper(BaseImageJHelper):
    def __init__(
        self, headless=False, bind=True, version="sc.fiji:fiji", plugins=[]
    ) -> None:
        if bind:
            set_running_helper(self)

        super().__init__(
            headless=headless, version="/home/jhnnsrs/Fiji.app", plugins=plugins
        )
