from concurrent.futures import ThreadPoolExecutor
import logging
from rekuest.actors.functional import (
    ThreadedFuncActor,
)
from rekuest.api.schema import ProvisionFragment, ProvisionFragmentTemplate, DefinitionFragment
from mikro.api.schema import (
    RepresentationFragment,
    RepresentationVarietyInput,
    from_xarray,
    from_df
)
from rekuest.definition.validate import auto_validate
from mikroj.macro_helper import ImageJMacroHelper
from mikroj.registries.base import Macro, RESULTS_KEY, ROIS_KEY, ACTIVE_OUT_KEY, ACTIVE_IN_KEY
from mikro.traits import Representation
import xarray as xr
from pydantic import Field


def jtranspile(
    instance,
    helper: ImageJMacroHelper,
):
    if isinstance(instance, Representation):
        x = helper.py.to_java(instance.data.squeeze().compute())
        properties = x.getProperties()
        properties.put("name", instance.name)
        properties.put("representation_id", instance.id)
        return x

    return instance


def ptranspile(
    instance,
    kwargs: dict,
    helper: ImageJMacroHelper,
    macro: Macro,
    definition: DefinitionFragment,
):

    if (
        instance.__class__.__name__ == "ij.ImagePlus"
        or instance.__class__.__name__ == "net.imagej.DefaultDataset"
        or instance.__class__.__name__ == "ij.CompositeImage"
    ):
        print(instance)
        xarray: xr.DataArray = helper.py.from_java(instance)
        print(xarray)
        if "row" in xarray.dims:
            xarray = xarray.rename(row="x")
        if "col" in xarray.dims:
            xarray = xarray.rename(col="y")
        if "Channel" in xarray.dims:
            xarray = xarray.rename(Channel="c")
            
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

        name = "Output of" + definition.name

        if len(origins) > 0:
            name = (
                definition.name
                + " of "
                + " , ".join(map(lambda x: x.name, origins))
            )

        rep = from_xarray(xarray, name=name, variety=type, origins=origins)

        return rep
    if instance.__class__.__name__ == "net.imagej.legacy.convert.ResultsTableWrapper":
       pdDataFrame = helper.py.from_java(instance)

       rep_origins = [
            arg for arg in kwargs.values() if isinstance(arg, RepresentationFragment)
       ]


       table = from_df(pdDataFrame, name=definition.name, rep_origins=rep_origins)
       return table




    return instance


class FuncMacroActor(ThreadedFuncActor):
    macro: Macro
    helper: ImageJMacroHelper
    threadpool: ThreadPoolExecutor = Field(
        default_factory=lambda: ThreadPoolExecutor(max_workers=1)
    )
    _validated_definition: DefinitionFragment

    async def on_provide(self, provision: ProvisionFragment):
        self._validated_definition = auto_validate(self.definition)
        return await super().on_provide(provision)

    def assign(self, **kwargs):
        logging.info("Being assigned")

        transpiled_args = {
            key: jtranspile(kwarg, self.helper) for key, kwarg in kwargs.items()
        }

        if self.macro.setactivein:
            image = transpiled_args.pop(self._validated_definition.args[0].key)
            self.helper.ui.show(
                kwargs[self._validated_definition.args[0].key].name, image
            )
        macro_output = self.helper.py.run_macro(self.macro.code, {**transpiled_args})
        print(macro_output)

        imagej_returns = []

        outkeys = [re.key for re in self._validated_definition.returns]

        for re in self._validated_definition.returns:
            if re.key == RESULTS_KEY:
                imagej_returns.append(self.helper.get_results_table())
                continue
            if re.key  == ROIS_KEY:
                imagej_returns.append(self.helper.get_rois())
                continue
            if re.key  == ACTIVE_OUT_KEY:
                imagej_returns.append(self.helper.py.active_imageplus())
                continue

            imagej_returns.append(macro_output.getOutput(re.key))


        transpiled_returns = [
            ptranspile(value, kwargs, self.helper, self.macro, self._validated_definition)
            for value in imagej_returns
        ]

        print(transpiled_returns)

        if len(transpiled_returns) == 0:
            return None
        if len(transpiled_returns) == 1:
            return transpiled_returns[0]
        
        return transpiled_returns

    class Config:
        underscore_attrs_are_private = True