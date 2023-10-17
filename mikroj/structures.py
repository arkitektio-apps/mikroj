import uuid
import xarray as xr
from rekuest.structures.registry import StructureRegistry
from rekuest.collection.shelve import get_current_shelve
from mikroj.bridge import ImageJBridge
from imagej._java import JObjectArray, jc


class ImageJPlus:
    def __init__(self, value, name, bridge: ImageJBridge) -> None:
        self.value = value
        self.name = name
        self.id = str(uuid.uuid4())
        self.bridge = bridge

    async def ashrink(self) -> "str":
        shelve = get_current_shelve()
        return await shelve.aput(self)

    def get_image_id(self):
        return self.value.getID()

    def get_as_label(self):
        return self.value.getOverlay()

    def close(self):
        self.value = self.bridge.ij.convert().convert(self.value, jc.ImagePlus)
        self.value.changes = False  # YEEEEESSSSSS FINALLY I CAN CLOSE IMAGES
        self.value.close()

    def to_jarg(self):
        return self.value

    @classmethod
    def from_jreturn(cls, value, bridge: ImageJBridge):
        return cls(value, str(uuid.uuid4()), bridge)

    @classmethod
    async def aexpand(cls, value: "str") -> None:
        shelve = get_current_shelve()
        return await shelve.aget(value)

    @classmethod
    async def acollect(cls, id):
        shelve = get_current_shelve()
        x = await shelve.aget(id)
        x.close()
        return await shelve.adelete(id)

    def to_xarray(self):
        xarray: xr.DataArray = self.bridge.py.from_java(self.value)
        if "row" in xarray.dims:
            xarray = xarray.rename(row="x")
        if "pln" in xarray.dims:
            xarray = xarray.rename(pln="z")
        if "ch" in xarray.dims:
            xarray = xarray.rename(ch="c")
        if "col" in xarray.dims:
            xarray = xarray.rename(col="y")
        if "Channel" in xarray.dims:
            xarray = xarray.rename(Channel="c")

        return xarray

    def set_active(self):
        self.bridge.ui.show(self.name, self.value)

    @classmethod
    def from_xarray(
        cls,
        data,
        name: str,
        bridge: ImageJBridge,
    ):
        image = bridge.py.to_dataset(data)

        return cls(image, name, bridge)


class ImageJStructureRegistry(StructureRegistry):
    pass
