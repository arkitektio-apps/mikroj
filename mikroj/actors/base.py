from arkitekt.actors.functional import (
    ThreadedFuncActor,
)
from arkitekt.api.schema import ProvisionFragment, ProvisionFragmentTemplate
from mikroj.macro_helper import ImageJMacroHelper
from mikroj.registries.base import Macro
from mikro.traits import Representation


def jtranspile(
    instance,
    helper: ImageJMacroHelper,
):
    if isinstance(instance, Representation):
        x = helper.py.to_java(instance.data.rename(x="y", y="x").squeeze().compute())
        print(x.__class__.__name__)
        return x

    return instance


def ptranspile(
    instance,
    helper: ImageJMacroHelper,
    macro: Macro,
    template: ProvisionFragmentTemplate,
):

    if instance.__class__.__name__ == "net.imagej.DefaultDataset":
        xarray = helper.py.from_java(instance)
        rep = Representation.objects.from_xarray(xarray)
        return rep

    if instance.__class__.__name__ == "ij.ImagePlus":
        xarray = helper.py.from_java(instance)

        rep = Representation.objects.from_xarray(
            xarray, name="Undetermined through MikroJ"
        )
        return rep

    return instance


class FuncMacroActor(ThreadedFuncActor):
    macro: Macro
    helper: ImageJMacroHelper

    async def on_provide(self, provision: ProvisionFragment):
        print("Being provided")
        return await super().on_provide(provision)

    def assign(self, *args, **kwargs):
        print("Being assigned")

        imagej_args = {
            port.key: jtranspile(arg, self.helper)
            for arg, port in zip(
                args, self.provision.template.node.args
            )  # TODO: unnnecssary back
        }
        imagej_kwargs = {
            key: jtranspile(kwarg, self.helper) for key, kwarg in kwargs.items()
        }

        if self.macro.setactivein:
            image = imagej_args.pop(self.provision.template.node.args[0].key)
            self.helper.ui.show(args[0].name, image)

        macro_output = self.helper.py.run_macro(
            self.macro.code, {**imagej_args, **imagej_kwargs}
        )

        imagej_returns = []

        if self.macro.takeactiveout:
            print("Taking old Image out")
            imagej_returns.append(self.helper.py.active_image_plus())

        for index, re in enumerate(self.provision.template.node.returns):
            if index == 0 and self.macro.takeactiveout:
                continue  # we already put the image out
            imagej_returns.append(macro_output.getOutput(re.key))

        transpiled_returns = [
            ptranspile(value, self.helper, self.macro, self.provision)
            for value in imagej_returns
        ]

        print(transpiled_returns)

        return (
            transpiled_returns if transpiled_returns else None
        )  # TODO: Non problamtic
