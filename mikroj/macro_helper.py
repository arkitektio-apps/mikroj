from typing import Optional
from pydantic import BaseModel, Field


class ImageJMacroHelper(BaseModel):
    maximum_memory: Optional[int] = Field(default=None)
    minimum_memory: Optional[int] = Field(default=None)

    _ij = None

    def set_ij_instance(self, ij):
        self._ij = ij

    @property
    def py(self):
        return self._ij.py

    @property
    def ui(self):
        return self._ij.ui()

    class Config:
        arbitary_types_allowed = True
        underscore_attrs_are_private = True
