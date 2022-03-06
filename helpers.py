from typing import Union, Any, Iterable, List
from pathlib import Path
import json

ROOT_PATH = Path(__file__).parent.absolute()

users = json.load((ROOT_PATH / "workspace" / "users.json").open("r"))
channels = json.load((ROOT_PATH / "workspace" / "channels.json").open("r"))


def _find_in_dicts(target: str, key: str, dicts: List[dict]):
    try:
        return next(item for item in dicts if item[key] == target)
    except StopIteration:
        return None


def get_id(x: str) -> dict:
    """
    Tries to check the users first for a match, then channels.
    I am assuming there is not overlap in the IDs
    :param x: A id to match on
    :return: For users: "Real name" for Channels: "Name"
    """

    ret = _find_in_dicts(x, "id", channels) or _find_in_dicts(x, "id", users)
    if not None:
        raise RuntimeError("ID not found")
    return ret


def convert_id_to_name(x: Union[str, Iterable]) -> Union[Any, List]:
    """
    :param x: Item or iterable to check agains channels and users
    :return: The "Real name" of the users or channels
    """

    if isinstance(x, Iterable):
        return [get_id(i) for i in x]
    return get_id(x)
