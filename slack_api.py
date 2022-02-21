#!/usr/bin/env python3
from typing import List, Dict
from pydantic import BaseModel

import slack_sdk
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

from cfg import config, auth
from loguru import logger
from functools import cache


class ConvoOverview(BaseModel):
    convo_testing: Dict
    convo_logging: Dict
    convo_adding: Dict
    convo_cleanup: List[Dict]


class Api:
    def __init__(self, token=None, live=False, test=False):
        self.live = live
        self.test = test

        if live:
            logger.warning("We are running in live mode, we will manipulate slack")
            if test:
                logger.error("Live and test can't be running at the same time")
                exit(1)
        elif test:
            logger.info("Running test mode (restricted channels and users)")
        else:
            logger.info("Running drymode")

        if token:
            self.api = slack_sdk.WebClient(token)
        else:
            self.api = slack_sdk.WebClient(auth.token)

        self.api.api_test()
        self.conversations()

    @cache
    def convo_testing(self):
        return self.conversations().convo_testing

    @cache
    def convo_logging(self):
        return self.conversations().convo_logging

    @cache
    def convo_adding(self):
        return self.conversations().convo_adding

    @cache
    def convo_cleanup(self):
        return self.conversations().convo_cleanup

    @cache
    def conversations(self) -> ConvoOverview:
        """
        Fetches the data for the conversations listed in channels.logging, channels.adding and channels.cleanup
        :return: { convo_logging: List[], convo_adding: List[], convo_clenaup: List[]}
        """

        convo_testing = None
        convo_logging = None
        convo_adding = None
        convo_cleanup = []

        logger.info("Fetching convos")
        resp = self.api.conversations_list(limit=1000, types="public_channel")
        conversations_all = resp.data["channels"]

        logger.info(f"Found {len(conversations_all)} convos")
        logger.info("Filtering...")

        for convo in conversations_all:
            name = convo["name"]
            id = convo["id"]

            if name == config.channels.logging:
                if convo_logging:
                    logger.critical("Found multiple matches for logging convo")
                    exit(1)
                convo_logging = convo
                logger.info(f"Found logging convo {id} {name}")

            elif name == config.channels.testing:
                if convo_testing:
                    logger.critical("Found multiple matches for testing convo")
                    exit(1)
                convo_testing = convo

            elif name in config.channels.adding:
                if convo_adding:
                    logger.critical("Found multiple matches for adding convo")
                    exit(1)
                convo_adding = convo
                logger.info(f"Found adding convo {id} {name}")

            elif name in config.channels.cleanup:
                convo_cleanup.append(convo)
                logger.info(f"Found cleanup convo {id} {name}")

        return ConvoOverview(
            **{
                "convo_logging": convo_logging,
                "convo_testing": convo_testing,
                "convo_adding": convo_adding,
                "convo_cleanup": convo_cleanup,
            }
        )

    def convo_join_silent(self, channel_id):
        self.api.conversations_join(channel=channel_id)

    def convo_dm_by_user_id(self, user_id):
        """
        Find the dm the app has had with the user
        :param user_id: The id
        :return: the channel object
        """

        resp = self.api.conversations_list(types="im", limit=1000)
        for channel in resp["channels"]:
            if channel["user"] == user_id:
                return channel

        raise RuntimeError

    def convo_list_members(self, channel_id) -> SlackResponse:
        return self.api.conversations_members(channel=channel_id, limit=1000)

    def convo_get_by_name(self, channel_name):
        for convo in self.conversations():
            if convo["name"] == channel_name:
                return convo

        raise RuntimeError("Unable to find channel")

    def convo_get(self, channel_id):
        return self.api.conversations_info(channel=channel_id)

    def convo_history(self, channel_id):
        return self.api.conversations_history(channel=channel_id)

    def user_get(self, user_id):
        return self.api.users_info(user=user_id)

    def user_remove(self, channel_id, user_id):
        logger.debug(f"Removing {user_id} from {channel_id}")

        if self.live:
            self.api.conversations_kick(channel=channel_id, user=user_id)
        elif self.test:
            assert channel_id == self.convo_testing()["id"]
            assert user_id == config.testing.user_test
            self.api.conversations_kick(channel=channel_id, user=user_id)

    def user_add(self, channel_id, user_id):
        logger.debug(f"Adding {user_id} to {channel_id}")

        try:

            if self.live:
                self.api.conversations_invite(channel=channel_id, users=user_id)
            elif self.test:
                assert channel_id == self.convo_testing()["id"]
                assert user_id == config.testing.user_test
                self.api.conversations_invite(channel=channel_id, users=user_id)

        except SlackApiError as e:
            if e.response.data["error"] != "already_in_channel":
                raise e

    def msg_user(self, user_id, msg):
        logger.debug(f"Sending {user_id} a msg")
        if self.live:
            self.api.chat_postMessage(channel=user_id, text=msg)
        elif self.test:
            assert user_id == config.testing.user_msg
            self.api.chat_postMessage(channel=user_id, text=msg)
