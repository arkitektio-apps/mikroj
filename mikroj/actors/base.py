from concurrent.futures import ThreadPoolExecutor
import logging
from rekuest.actors.functional import (
    ThreadedFuncActor,
)
from rekuest.api.schema import ProvisionFragment, ProvisionFragmentTemplate
from mikro.api.schema import (
    RepresentationFragment,
    RepresentationVarietyInput,
    from_xarray,
)
from mikroj.macro_helper import ImageJMacroHelper
from mikroj.registries.base import Macro
from mikro.traits import Representation
import xarray as xr
from pydantic import Field


def jtranspile(
    instance,
    helper: ImageJMacroHelper,
):
    if isinstance(instance, Representation):
        x = helper.py.to_java(instance.data.rename(x="y", y="x").squeeze().compute())

        return x

    return instance


def ptranspile(
    instance,
    kwargs: dict,
    helper: ImageJMacroHelper,
    macro: Macro,
    provision: ProvisionFragment,
):

    if (
        instance.__class__.__name__ == "ij.ImagePlus"
        or instance.__class__.__name__ == "net.imagej.DefaultDataset"
    ):
        xarray: xr.DataArray = helper.py.from_java(instance).rename(Channel="c")
        if "c" in xarray.dims:
            if xarray.sizes["c"] == 3:
                type = (
                    RepresentationVarietyInput.RGB
                    if macro.rgb
                    else RepresentationVarietyInput.VOXEL
                )
            else:
                type = RepresentationVarietyInput.VOXEL
        else:
            type = RepresentationVarietyInput.VOXEL

        origins = [
            arg for arg in kwargs.values() if isinstance(arg, RepresentationFragment)
        ]
        tags = []
        if macro.filter:
            tags = tags.append("filtered")

        name = "Output of" + provision.template.node.name

        if len(origins) > 0:
            name = (
                provision.template.node.name
                + " of "
                + " , ".join(map(lambda x: x.name, origins))
            )

        rep = from_xarray(xarray, name=name, variety=type, origins=origins)

        return rep

    return instance


class FuncMacroActor(ThreadedFuncActor):
    macro: Macro
    helper: ImageJMacroHelper
    threadpool: ThreadPoolExecutor = Field(
        default_factory=lambda: ThreadPoolExecutor(max_workers=1)
    )

    async def on_provide(self, provision: ProvisionFragment):
        logging.info("Being provided")
        return await super().on_provide(provision)

    def assign(self, **kwargs):
        logging.info("Being assigned")

        transpiled_args = {
            key: jtranspile(kwarg, self.helper) for key, kwarg in kwargs.items()
        }

        if self.macro.setactivein:
            image = transpiled_args.pop(self.provision.template.node.args[0].key)
            self.helper.ui.show(
                kwargs[self.provision.template.node.args[0].key].name, image
            )
        macro_output = self.helper.py.run_macro(self.macro.code, {**transpiled_args})

        imagej_returns = []

        if self.macro.takeactiveout:
            imagej_returns.append(self.helper.py.active_image_plus())

        for index, re in enumerate(self.provision.template.node.returns):
            if index == 0 and self.macro.takeactiveout:
                continue  # we already put the image out
            imagej_returns.append(macro_output.getOutput(re.key))

        transpiled_returns = [
            ptranspile(value, kwargs, self.helper, self.macro, self.provision)
            for value in imagej_returns
        ]

        if len(transpiled_returns) == 0:
            return None
        if len(transpiled_returns) == 1:
            return transpiled_returns[0]
        else:
            return transpiled_returns
