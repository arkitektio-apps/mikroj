from abc import abstractclassmethod, abstractmethod
from arkitekt.packers.structure import BoundType, Structure, StructureMeta
import uuid
from mikro.schema import Representation

from mikroj.structures.store import get_current_memory


class ImagePlus(Structure):
    """Image Plus BETA

    Fiji Image is an Agent bounc Structure that represent an in Memory open
    image on Fiji. It provides easy conversion to

    Args:
        Structure ([type]): [description]
    """

    def __init__(self, image, reference=None) -> None:
        self.image = image
        self.reference = reference or uuid.uuid4()
        super().__init__()

    @classmethod
    def get_structure_meta(cls) -> StructureMeta:
        return StructureMeta(bound=BoundType.AGENT, identifier="imageplus")

    @classmethod
    async def expand(cls, shrinked_value):
        return await get_current_memory().get(shrinked_value)

    async def shrink(self):
        return await get_current_memory().put(self.reference, self.image)
