import pytest


from slack_sdk.errors import SlackApiError

from slack_api import Api

from tests.common import auth, config

_ = auth
_ = config


@pytest.fixture(autouse=True, scope="session")
def api(auth, config):
    return Api(auth.token, test=True)


def test_conversations(config, api):
    ret = api.conversations()
    print(ret)


def test_dm(config, api):
    test_user_id = config.testing.user_msg

    noise = api.session_id
    msg = config.message + f"\n\n\nID:{noise}"

    api.msg_user(test_user_id, msg)

    resp = api.convo_dm_by_user_id(test_user_id)
    channel_id = resp["id"]

    history = api.convo_history(channel_id)

    assert history.data["messages"][0]["text"] == msg


def test_dm_msg(config, api):
    api.msg_user_config_message(config.testing.user_msg)
    with pytest.raises(RuntimeError):
        api.msg_user_config_message(config.testing.user_msg)


def test_user_channel_test_add(config, api):
    target_channel = api.convo_testing()
    target_user_id = config.testing.user_test

    api.convo_join_silent(target_channel["id"])

    api.user_add(channel_id=target_channel["id"], user_id=target_user_id)

    resp = api.convo_list_members(target_channel["id"])
    members = resp.data["members"]

    assert target_user_id in members


@pytest.mark.order(after="test_user_channel_test_add")
def test_user_channel_test_remove(config, auth, api):
    target_channel = api.convo_testing()
    target_user_id = config.testing.user_test
    api.convo_join_silent(target_channel["id"])

    resp = api.convo_list_members(target_channel["id"])
    members = resp.data["members"]
    assert target_user_id in members, "User we want to kick not in members"

    api.user_remove(channel_id=target_channel["id"], user_id=target_user_id)

    resp = api.convo_list_members(target_channel["id"])
    members = resp.data["members"]
    assert target_user_id not in members, "User we want to kick still there"


@pytest.mark.order(after="test_user_channel_test_remove")
def test_user_channel_test_remove_twice(config, auth, api):
    target_channel = api.convo_testing()
    target_user_id = config.testing.user_test
    with pytest.raises(SlackApiError):
        api.user_remove(channel_id=target_channel["id"], user_id=target_user_id)


def test_list_channels(config, auth, api):
    assert api.convo_testing()
    assert api.convo_logging()
    assert api.convo_adding()
    assert api.convo_cleanup()
