import imagej
import scyjava
import scyjava
import xarray as xr
import dask
from mikro import Representation
import os


class BaseImageJHelper:
    def __init__(
        self, headless=False, version="2.1.0", plugins=[], plugins_dir="plugins"
    ) -> None:
        # concatenade version plus plugins
        # build = [version] + plugins if len(plugins) > 0 else version
        # if plugins_dir:
        #   path = os.path.join(os.getcwd(),plugins_dir)
        #    scyjava.config.add_option(f'-Dplugins.dir={path}')

        self.headless = headless
        print(f"Initializing with version {version}")
        plugins_dir = "/home/jhnnsrs/Fiji.app/plugins"
        scyjava.config.add_option(f"-Dplugins.dir={plugins_dir}")

        self._ij = imagej.init(version, headless=headless)
        if not headless:
            self._ij.ui().showUI()
        super().__init__()

    @property
    def py(self):
        return self._ij.py

    @property
    def ui(self):
        return self._ij.ui()

    @property
    def ij(self):
        return self._ij

    def show_xarray(self, xarray: xr.DataArray):
        if dask.is_dask_collection(xarray.data):
            jimage = self.py.to_java(xarray.compute())
        else:
            jimage = self.py.to_java(xarray)

        self.ui.show(xarray.name, jimage)

    def displayRep(self, rep: Representation):
        image = rep.data.squeeze()

        if dask.is_dask_collection(image.data):
            jimage = self.py.to_java(image.compute())
        else:
            jimage = self.py.to_java(image)

        # Convert the Image to Image
        self.ui.show(rep.name, jimage)


RUNNING_HELPER = None


def get_running_helper() -> BaseImageJHelper:
    global RUNNING_HELPER
    if RUNNING_HELPER is None:
        print("Happening")
        RUNNING_HELPER = BaseImageJHelper()
    return RUNNING_HELPER


def set_running_helper(instance: BaseImageJHelper):
    global RUNNING_HELPER
    RUNNING_HELPER = instance
