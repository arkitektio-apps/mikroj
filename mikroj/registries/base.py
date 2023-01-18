from typing import List
from pydantic import BaseModel

ACTIVE_OUT_KEY = "active_out"
ACTIVE_IN_KEY = "active_in"
RESULTS_KEY = "results"
ROIS_KEY = "rois"



class Macro(BaseModel):
    code: str
    name: str
    interfaces: List[str]
    description: str
    setactivein: bool = False  # mirorring CellProfiler approach
    takeactiveout: bool = False
    donecloseactive: bool = False
    interactive: bool = False
    getroisout: bool = False
    getresults: bool = False
    filter: bool = False
    rgb: bool = False
