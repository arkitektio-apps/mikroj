import uuid
import xarray as xr
from rekuest.structures.registry import StructureRegistry
from rekuest.collection.shelve import get_current_shelve
from mikroj.macro_helper import ImageJMacroHelper


class ImageJPlus:
    def __init__(self, value, name) -> None:
        self.value = value
        self.name = name
        self.id = str(uuid.uuid4())

    async def ashrink(self) -> "str":
        shelve = get_current_shelve()
        return await shelve.aput(self)

    def get_image_id(self):
        return self.value.getID()

    def close(self):
        self.value.close()

    def to_jarg(self, helper):
        return self.value

    @classmethod
    def from_jreturn(cls, value, helper):
        return cls(value, str(uuid.uuid4()))

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

    def to_xarray(self, helper: ImageJMacroHelper):
        xarray: xr.DataArray = helper.py.from_java(self.value)
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

    def set_active(self, helper: ImageJMacroHelper):
        helper.ui.show(self.name, self.value)

    @classmethod
    def from_xarray(
        cls,
        data,
        name: str,
        helper: ImageJMacroHelper,
    ):
        image = helper.py.to_imageplus(helper.py.to_java(data))
        return cls(image, name)


class ImageJStructureRegistry(StructureRegistry):
    pass
