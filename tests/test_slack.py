import pytest

from random import sample
from string import ascii_lowercase

from slack_api import Api
from loguru import logger

from tests.common import auth, config

_ = auth
_ = config


@pytest.fixture(autouse=True, scope="session")
def api(auth, config):
    return Api(auth.token, test=True)


def test_dm(config, api):
    test_user_id = config.testing.user_msg

    noise = "".join(sample(ascii_lowercase, 4))
    msg = config.message + f"\n\n\nID:{noise}"

    api.msg_user(test_user_id, msg)

    resp = api.convo_dm_by_user_id(test_user_id)
    channel_id = resp["id"]

    history = api.convo_history(channel_id)

    assert history.data["messages"][0]["text"] == msg


def test_user_channel_test_add(config, api):
    target_channel = api.convo_testing()
    target_user_id = config.testing.user_test

    api.convo_join_silent(target_channel["id"])

    api.user_add(target_channel["id"], target_user_id)

    resp = api.convo_list_members(target_channel["id"])
    members = resp.data["members"]

    assert target_user_id in members


# TODO: Remove test will fail untill the app gets the access it needs..
@pytest.mark.order(after="test_user_channel_test_add")
def test_user_channel_test_remove(config, auth, api):
    target_channel = api.convo_testing()
    target_user_id = config.testing.user_test
    api.convo_join_silent(target_channel["id"])

    resp = api.convo_list_members(target_channel["id"])
    members = resp.data["members"]
    assert target_user_id in members, "User we want to kick not in members"

    api.user_remove(target_channel["id"], target_user_id)

    resp = api.convo_list_members(target_channel["id"])
    members = resp.data["members"]
    assert target_user_id not in members, "User we want to kick still there"


def test_list_channels(config, auth, api):
    assert api.convo_testing()
    assert api.convo_logging()
    assert api.convo_adding()
    assert api.convo_cleanup()
