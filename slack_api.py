#!/usr/bin/env python3

import slack_sdk
from config import config, auth
from functools import lru_cache


class Api:
    def __init__(self):
        self.api = slack_sdk.WebClient(auth.token)
        self.api.api_test()

    @lru_cache()
    def conversations(self):
        return self.api.conversations_list()

    @lru_cache()
    def find_users(self):
        return self.api.users_list()
