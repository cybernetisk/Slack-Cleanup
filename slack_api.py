#!/usr/bin/env python3
import random
import time
from typing import List, Dict
from pydantic import BaseModel

import slack_sdk
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

import helpers
from cfg import config, auth
from loguru import logger
from functools import cache

from string import ascii_lowercase

from retry import retry


class UserNotFoundException(Exception):
    pass


class MsgSentException(Exception):
    pass


class ConvoOverview(BaseModel):
    convo_testing: Dict
    convo_logging: Dict
    convo_adding: List[Dict]
    convo_cleanup: List[Dict]


def handle_rate_limit(e):
    if e.response.data["error"] == "ratelimited":
        timeout = int(e.response.headers["Retry-After"])
        timeout = int(timeout * 1.4)
        logger.debug(f"Ratelimited. Waiting {timeout}")
        time.sleep(int(timeout))


class Api:
    def __init__(self, token=None, live=False, test=False):
        self.live = live
        self.test = test
        self.session_id = "".join(random.sample(ascii_lowercase, 10))

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
    def convo_testing(self) -> dict:
        return self.conversations().convo_testing

    @cache
    def convo_logging(self) -> dict:
        return self.conversations().convo_logging

    @cache
    def convo_adding(self) -> List[dict]:
        return self.conversations().convo_adding

    @cache
    def convo_cleanup(self) -> List[dict]:
        return self.conversations().convo_cleanup

    # TODO: Download new export
    def conversations(self) -> ConvoOverview:
        """
        :return: { convo_logging: List[], convo_adding: List[], convo_clenaup: List[]}
        """

        convo_logging = helpers.get_name_obj(config.channels.logging)
        convo_testing = helpers.get_name_obj(config.channels.testing)
        convo_adding = [helpers.get_name_obj(c) for c in config.channels.adding]
        convo_cleanup = [helpers.get_name_obj(c) for c in config.channels.cleanup]

        return ConvoOverview(
            **{
                "convo_logging": convo_logging,
                "convo_testing": convo_testing,
                "convo_adding": convo_adding,
                "convo_cleanup": convo_cleanup,
            }
        )

    def convo_join_silent(self, channel_id):
        """
        Makes the bot join the channel
        :param channel_id: The ID of the channel we should join
        """
        if self.live:
            logger.info(f"Joining {channel_id}")
            self.api.conversations_join(channel=channel_id)
        elif self.test:
            assert channel_id == self.convo_testing()["id"]
            self.api.conversations_join(channel=channel_id)
        else:
            logger.info(f"[DRY] Joining {channel_id}")

    @retry(SlackApiError, tries=2)
    def convo_dm_by_user_id(self, user_id):
        """
        Find the dm the app has had with the user
        :param user_id: The id
        :return: the channel object
        """

        try:
            resp = self.api.conversations_list(types="im", limit=1000)
        except SlackApiError as e:
            handle_rate_limit(e)
            raise e

        for channel in resp["channels"]:
            if channel["user"] == user_id:
                return channel

        raise UserNotFoundException

    @retry(SlackApiError, tries=2)
    def convo_list_members(self, channel_id) -> SlackResponse:
        try:
            return self.api.conversations_members(channel=channel_id, limit=1000)
        except SlackApiError as e:
            handle_rate_limit(e)
            raise e

    @retry(SlackApiError, tries=2)
    def convo_get(self, channel_id):
        try:
            return self.api.conversations_info(channel=channel_id)
        except SlackApiError as e:
            handle_rate_limit(e)
            raise e

    @retry(SlackApiError, tries=2)
    def convo_history(self, channel_id):
        try:
            return self.api.conversations_history(channel=channel_id)
        except SlackApiError as e:
            handle_rate_limit(e)
            raise e

    @retry(SlackApiError, tries=2)
    def user_get(self, user_id):
        try:
            return self.api.users_info(user=user_id)
        except SlackApiError as e:
            handle_rate_limit(e)
            raise e

    @retry(SlackApiError, tries=2)
    def user_remove(self, *, channel_id, user_id):
        username = helpers.convert_id_to_name(user_id)
        channel_name = helpers.convert_id_to_name(channel_id)

        if self.live:
            logger.debug(f"Removing {username} from {channel_name}")
            try:
                self.api.conversations_kick(channel=channel_id, user=user_id)
            except SlackApiError as e:
                handle_rate_limit(e)
                raise e
        elif self.test:
            assert channel_id == self.convo_testing()["id"]
            assert user_id == config.testing.user_test
            self.api.conversations_kick(channel=channel_id, user=user_id)
        else:
            logger.debug(f"[DRY] Removing {username} from {channel_name}")

    @retry(SlackApiError, tries=2)
    def user_add(self, *, channel_id, user_id):
        username = helpers.convert_id_to_name(user_id)
        channel_name = helpers.convert_id_to_name(channel_id)
        try:
            if self.live:
                logger.debug(f"Adding {username} to {channel_name}")
                try:
                    self.api.conversations_invite(channel=channel_id, users=user_id)
                except SlackApiError as e:
                    handle_rate_limit(e)
                    raise e
            elif self.test:
                assert channel_id == self.convo_testing()["id"]
                assert user_id == config.testing.user_test
                self.api.conversations_invite(channel=channel_id, users=user_id)
            else:
                logger.debug(f"[DRY] Adding {username} to {channel_name}")

        except SlackApiError as e:
            if e.response.data["error"] != "already_in_channel":
                raise e

    @retry(SlackApiError, tries=2)
    def msg_user_config_message(self, user_id):
        try:
            resp = self.convo_dm_by_user_id(user_id)
            channel_id = resp["id"]
            history = self.convo_history(channel_id)

            messages = history.data["messages"]
            if len(messages) == 0:
                logger.info("No messages found with user")
            elif self.session_id in messages[0]["text"]:
                logger.info("Msg already sent")
                raise MsgSentException("Msg already sent")
        except UserNotFoundException as e:
            logger.info("No convo found with bot")

        noise = self.session_id
        msg = config.message + f"\n\n\nID:{noise}"
        self.msg_user(user_id, msg)

    @retry(SlackApiError, tries=2)
    def msg_user(self, user_id, msg):
        username = helpers.convert_id_to_name(user_id)
        if self.live:
            logger.debug(f"Sending {username} a msg")
            try:
                self.api.chat_postMessage(channel=user_id, text=msg)
            except SlackApiError as e:
                handle_rate_limit(e)
                raise e
        elif self.test:
            assert user_id == config.testing.user_msg
            self.api.chat_postMessage(channel=user_id, text=msg)
        else:
            logger.debug(f"[DRY] Sending {username} a msg")
