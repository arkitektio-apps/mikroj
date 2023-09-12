from typing import List
import re
from .types import Macro, Parameter, Context

doc = re.compile("\/\*(?P<name>(.|\n)*)\*\/*")

documentation = re.compile(
    "\/\*\W*(?P<name>[^\n]*)\n\W*(?P<description>[^\/\@]*)\n*\*.*"
)  # matches the first line in a docstring

in_re = re.compile("#@\W(?P<type>\w*)\W*(?P<key>\w*)")
return_re = re.compile("#@output\W(?P<type>\w*)\W*(?P<key>\w*)")

is_interactive_re = re.compile(".*@interactive*")
activein_re = re.compile(".*\@setactivein.*")
interfaces_re = re.compile(".*@interface:(\w*)\n")
activeout_re = re.compile(".*\@takeactiveout*")
getroisout_re = re.compile(
    ".*\@getroisout*"
)  # should we extract the rois from the roi manager?
getresults_re = re.compile(
    ".*\@getresults*"
)  # should we extract the results from the results table?


donecloseactive_re = re.compile(".*\@donecloseactive*")
filter_re = re.compile(".*\@filter*")
rgb_re = re.compile(".*\@rgb*")


params_re = re.compile(r"#@[^\(]*\((?P<params>[^\)]*)\)")  # line has params


def parse_parameters(code: str, output=False) -> List[Parameter]:
    """Checks for parameters in the code

    Will parse the macro code for parameters. If the output flag is set to True,
    it will parse for output parameters.

    Parameters
    ----------
    code : str
        The Macro Code
    output : bool, optional
        Parse outputs instead of inputs, by default False

    Returns
    -------
    List[Parameter]
        The list of parameters
    """
    if not output:
        matches = re.findall(r"#@ (?!output)(\w+) \((.*?)\) ?([\w]*)?", code)
    else:
        matches = re.findall(r"#@output (\w+)(?: \((.*?)\))? ?([\w]*)?", code)
    param_dicts = []

    for match in matches:
        param_type, param_str, key = match

        # Use regex to split on parameters
        param_items = re.findall(r"(\w+)=(\"[^\"]+\"|\w+)", param_str)

        # Convert to a dictionary
        param_dict = {"type": param_type, "key": key}
        for key, value in param_items:
            # Remove quotes if they exist
            param_dict[key] = value.strip('""')

        param_dicts.append(param_dict)

    return [
        Parameter(
            **param_dict,
        )
        for param_dict in param_dicts
    ]


def parse_context(code: str) -> Context:
    return Context(
        setactivein=bool(activein_re.search(code)),
        activeout=bool(activeout_re.search(code)),
        getroisout=bool(getroisout_re.search(code)),
        getresults=bool(getresults_re.search(code)),
        filter=bool(filter_re.search(code)),
        rgb=bool(rgb_re.search(code)),
    )


def parse_macro(code: str) -> Macro:
    d = documentation.match(code)

    m = Macro(
        code=code,
        name=d.group("name") if d else None,
        description=d.group("description") if d else None,
        context=parse_context(code),
        inputs=parse_parameters(code, output=False),
        outputs=parse_parameters(code, output=True),
    )
    return m
