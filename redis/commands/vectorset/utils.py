import json

from redis._parsers.helpers import pairs_to_dict
from redis.commands.vectorset.commands import CallbacksOptions


def parse_vemb_result(response, **options):
    """
    Handle VEMB result since the command can returning different result
    structures depending on input options and on quantization type of the vector set.

    Parsing VEMB result into:
    - List[Union[bytes, Union[int, float]]]
    - Dict[str, Union[bytes, str, float]]
    """
    pass


def parse_vlinks_result(response, **options):
    """
    Handle VLINKS result since the command can be returning different result
    structures depending on input options.
    Parsing VLINKS result into:
    - List[List[str]]
    - List[Dict[str, Number]]
    """
    pass


def parse_vsim_result(response, **options):
    """
    Handle VSIM result since the command can be returning different result
    structures depending on input options.
    Parsing VSIM result into:
    - List[List[str]]
    - List[Dict[str, Number]] - when with_scores is used (without attributes)
    - List[Dict[str, Mapping[str, Any]]] - when with_attribs is used (without scores)
    - List[Dict[str, Union[Number, Mapping[str, Any]]]] - when with_scores and with_attribs are used

    """
    pass
