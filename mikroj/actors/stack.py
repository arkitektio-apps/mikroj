from mikroj.actors.base import FuncMacroActor
from mikro import Representation
from mikroj.registries.actor import register_macro_actor
import dask

@register_macro_actor("stacktostack")
class StackToStackActor(FuncMacroActor):
    

    async def assign(self, rep: Representation):
        """[summary]

        Args:
            rep (Representation): [description]

        Returns:
            [type]: [description]
        """
        helper = self.helper
        image = rep.data.squeeze()
        # check if we are having a dask array
        if dask.is_dask_collection(image.data):
            jimage = helper.py.to_java(image.compute())
        else:
            jimage = helper.py.to_java(image)
        # Convert the Image to Image
        if not helper.headless: helper.ui.show(image.name, jimage)

        await self.run_macro()

        # open synchronized image
        imp = helper.py.active_image_plus()
        array = helper.py.from_java(imp)
        if "Channel" in array.dims: array = array.rename({"Channel": "c"})
        return Representation.asyncs.from_xarray(array)

