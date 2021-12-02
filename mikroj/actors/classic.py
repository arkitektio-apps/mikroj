from threading import active_count
from mikroj.actors.base import FuncMacroActor
from mikro import Representation
import dask

from mikroj.registries.helper import BaseImageJHelper, get_running_helper


def jtranspile(instance, helper: BaseImageJHelper):
    if isinstance(instance, Representation):
        x = helper.py.to_java(instance.data.squeeze().compute())
        print(x.__class__.__name__)
        return x

    return instance


def expand_xarray(xarray):
    if "z" not in xarray.dims:
        xarray = xarray.expand_dims("z")
    if "t" not in xarray.dims:
        xarray = xarray.expand_dims("t")
    if "c" not in xarray.dims:
        xarray = xarray.expand_dims("c")

    return xarray


def ptranspile(instance, helper: BaseImageJHelper):

    if instance.__class__.__name__ == "net.imagej.DefaultDataset":
        xarray = helper.py.from_java(instance)
        rep = Representation.objects.from_xarray(
            expand_xarray(xarray), name="Created from"
        )
        return rep

    if instance.__class__.__name__ == "ij.ImagePlus":
        xarray = helper.py.from_java(instance)
        rep = Representation.objects.from_xarray(
            expand_xarray(xarray), name="Created from"
        )
        return rep

    return instance


class ClassicMacroActor(FuncMacroActor):
    def assign(self, *args, **kwargs):
        """[summary]

        Args:
            rep (Representation): [description]

        Returns:
            [type]: [description]


        """

        from mikroj.registries.macro import get_current_macro_registry

        definition = get_current_macro_registry().get_definition_for_interface(
            self.template.node.interface
        )

        helper = get_running_helper()

        imagej_args = {
            port.key: jtranspile(arg, helper)
            for arg, port in zip(args, self.template.node.args)
        }
        imagej_kwargs = {
            key: jtranspile(kwarg, helper) for key, kwarg in kwargs.items()
        }

        if definition.setactivein:
            print("Setting Active")
            image = imagej_args.pop("image")
            helper.ij.ui().show(args[0].name, image)

        print(definition)

        print(imagej_args, imagej_kwargs)

        value = helper.ij.py.run_macro(
            definition.macro, {**imagej_args, **imagej_kwargs}
        )

        returns = []
        if definition.takeactiveout:
            returns.append(helper.py.active_image_plus())

        for index, re in enumerate(self.template.node.returns):
            if index == 0 and definition.takeactiveout:
                continue  # we already put the image out
            returns.append(value.getOutput(re.key))

        return tuple([ptranspile(value, helper) for value in returns])
