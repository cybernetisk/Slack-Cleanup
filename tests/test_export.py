import pytest

from tests.common import auth, config
from export import Export

_ = auth
_ = config


@pytest.fixture(autouse=True, scope="session")
def export() -> Export:
    return Export()


def test_export(export: Export, config):
    assert len(export.rooms.keys()) == len(config.channels.cleanup)


def test_get_room_json(export: Export, config):
    # cat * | jq ' . | length' | sort -n | paste -sd+
    room = export.get_room_json("cyb50")
    assert len(room) == 1137


def test_parse_room(export: Export, config):
    data = export.parse_room("cyb50")
    print(data)


def test_filter_on_age(export: Export, config):
    data = export.parse_room("studielabben")
    assert len(data) == 9

    to_be_removed = export.filter_on_age(data, config.timeout)
    assert len(to_be_removed.keys()) == 9
