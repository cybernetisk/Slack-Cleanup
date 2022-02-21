#!/usr/bin/env python3
from typing import List, Dict, Any
from pydantic import BaseModel

import slack_sdk


from cfg import config, auth
from loguru import logger
from functools import cache


class ConvoOverview(BaseModel):
    convo_logging: Dict
    convo_adding: Dict
    convo_cleanup: List[Dict]


class Api:
    def __init__(self, token=None, live=False):
        self.live = live
        self.conversations_all = List[Dict[Any, Any]]

        if live:
            logger.warning("We are running in live mode, we will manipulate slack")
        else:
            logger.info("Running drymode")

        if token:
            self.api = slack_sdk.WebClient(token)
        else:
            self.api = slack_sdk.WebClient(auth.token)

        self.api.api_test()
        self.conversations()

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

        convo_logging = None
        convo_adding = None
        convo_cleanup = []

        logger.info("Fetching convos")
        resp = self.api.conversations_list(limit=1000, types="public_channel")
        self.conversations_all = resp.data["channels"]

        logger.info(f"Found {len(self.conversations_all)} convos")
        logger.info("Filtering...")

        for convo in self.conversations_all:
            name = convo["name"]
            id = convo["id"]
            if name in config.channels.logging:
                if convo_logging:
                    logger.critical("Found multiple matches for logging convo")
                    exit(1)
                convo_logging = convo
                logger.info(f"Found logging convo {id} {name}")

            elif name in config.channels.adding:
                if self.convo_adding:
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
                "convo_adding": convo_adding,
                "convo_cleanup": convo_cleanup,
            }
        )

    def convo_list_members(self, channel_id):
        self.api.conversations_list()

    def user_remove(self, channel_id, user):
        # TODO
        raise NotImplementedError

    def user_add(self, channel_id, user):
        # TODO
        raise NotImplementedError

    def msg_user(self, user, msg):
        # TODO
        raise NotImplementedError

    def find_users(self):
        # TODO
        return self.api.users_list()
