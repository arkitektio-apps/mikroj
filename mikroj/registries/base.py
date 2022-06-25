from typing import List
from pydantic import BaseModel


class Macro(BaseModel):
    code: str
    name: str
    interfaces: List[str]
    description: str
    setactivein: bool = False  # mirorring CellProfiler approach
    takeactiveout: bool = False
    donecloseactive: bool = False
    interactive: bool = False
    filter: bool = False
