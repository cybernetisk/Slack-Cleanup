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


def test_convert_epoch():
    obj = helpers.convert_epoch_to_date(1646588871.00)
    assert "2022-03-06" == obj


def test_convert_epoch_list():
    obj = helpers.convert_epoch_to_date([1646588871.00, 1626538871.00])
    assert ["2022-03-06", "2021-07-17"] == obj


def test_convert_dict():
    d = {
        "U09QJN4RF": 1524034852.000361,
        "U4MDY3DP1": 1490094714.272758,
        "U4BKH50H2": 1490094639.257643,
    }

    t = {
        "andrnha": "2018-04-18",
        "pdthorsr": "2017-03-21",
        "annambu": "2017-03-21",
    }

    obj = helpers.convert_dict_to_name_and_date(d)
    assert t == obj
