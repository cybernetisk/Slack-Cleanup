import pytest

from slack_api import Api
from loguru import logger

from tests.common import auth, config

_ = auth
_ = config


@pytest.fixture(autouse=True, scope="session")
def api(auth, config):
    return Api(auth.token)


def test_dm(config, auth, api):
    logging_channel = api.convo_logging()
    test_user = config.testing.user_msg


def user_channel_test(config, auth, api):
    pass


def test_list_channels(config, auth, api):
    assert api.convo_logging()
    assert api.convo_adding()
    assert api.convo_cleanup()
