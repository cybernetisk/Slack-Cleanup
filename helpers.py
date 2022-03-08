from typing import Union, Iterable, List
from pathlib import Path
import datetime
import json


ROOT_PATH = Path(__file__).parent.absolute()

users = json.load((ROOT_PATH / "workspace" / "users.json").open("r"))
channels = json.load((ROOT_PATH / "workspace" / "channels.json").open("r"))


def _find_in_dicts(target: str, key: str, dicts: List[dict]):
    try:
        return next(item for item in dicts if item[key] == target)
    except StopIteration:
        return None


def get_name_obj(x: str) -> dict:
    return _find_in_dicts(x, "name", channels) or _find_in_dicts(x, "name", users)


def get_id_obj(x: str) -> dict:
    return _find_in_dicts(x, "id", channels) or _find_in_dicts(x, "id", users)


def get_id(x: str) -> str:
    """
    Tries to check the users first for a match, then channels.
    I am assuming there is not overlap in the IDs
    :param x: A id to match on
    :return: For users: "Real name" for Channels: "Name"
    """

    ret = _find_in_dicts(x, "id", channels)
    if ret:
        return ret["name"]
    ret = _find_in_dicts(x, "id", users)
    if ret:
        return ret["name"]

    raise RuntimeError("ID not found")


def convert_id_to_name(x: Union[str, Iterable]) -> Union[str, List]:
    """
    :param x: Item or iterable to check agains channels and users
    :return: The "Real name" of the users or channels
    """

    if isinstance(x, str):
        return get_id(x)

    if isinstance(x, Iterable):
        return [get_id(i) for i in x]

    return get_id(x)


def convert_epoch(x: float):
    return datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d")


def convert_epoch_to_date(x: Union[float, Iterable]) -> Union[str, List]:
    if isinstance(x, Iterable):
        return [convert_epoch(i) for i in x]

    return convert_epoch(x)


def convert_dict_to_name_and_date(x: dict) -> dict:
    d = {}

    for k, v in x.items():
        d[convert_id_to_name(k)] = convert_epoch_to_date(v)

    return d
