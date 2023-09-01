from mikroj.language.parse import parse_macro
from mikroj.language.define import define_macro
from mikroj import constants


def test_serialize_parameters(parameters):
    macro = parse_macro(parameters)
    assert macro.inputs[0].key == "m"


def test_define_analyze_particles(analyze_particles, transpile_registry):
    macro = parse_macro(analyze_particles)
    assert macro.inputs[0].key == "minSize"
    definition = define_macro(macro, transpile_registry)
    assert definition.name == "Particle Analyzer"
    assert definition.args[0].key == "active_in"
    assert definition.args[0].identifier == constants.IMAGEJ_PLUS_IDENTIFIER
