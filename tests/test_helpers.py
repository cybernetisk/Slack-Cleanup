import pytest

import helpers


def test_get_id_user():
    obj = helpers.convert_id_to_name("U03SNA4F0")
    assert obj == "nikolasp"


def test_get_id_user_list():
    obj = helpers.convert_id_to_name(["U03SNA4F0", "U02KRH15ZBK"])
    assert obj == ["nikolasp", "nikolasp998"]


def test_get_id_channel():
    obj = helpers.convert_id_to_name("C03QFBJ7U")
    assert obj == "generelt"


def test_get_id_channel_list():
    obj = helpers.convert_id_to_name(["C03QFGH34", "C03QFBJ7U"])
    assert obj == ["kafé", "generelt"]


def test_convert_id_fail():
    with pytest.raises(RuntimeError):
        helpers.convert_id_to_name("XXX")


def test_convert_id_list_fail():
    with pytest.raises(RuntimeError):
        helpers.convert_id_to_name(["XXX", "YYY"])
