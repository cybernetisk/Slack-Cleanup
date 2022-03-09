#!/usr/bin/env python3
from pathlib import Path
import json
from typing import List

from cfg import config
from loguru import logger

import datetime

from helpers import ROOT_PATH

# This file parses the workspace files to figure out which users not been active for a while

"""
For folder from config.cleanup:
    Read all messages
    For each message get:
        Poster and TS
        Repliers and latest_reply ts (not needed, thread posts are also posts)
        
        Reactions, use poster TS
        


Relevant fields from the struct:
{
    user: UserID
    ts: epoch
    
    reactions: [ {users: List[UserID]} ]

    reply_users: List[UserID]
    latests_reply: epoch
}

"""


class Export:
    def __init__(self):
        self.rooms: dict[str, list] = self.get_parsed_rooms()

    def get_parsed_rooms(self):
        rooms = {}

        for room in config.channels.cleanup:
            logger.info(f"Parsing {room}")
            json = self.get_room_json(room)
            logger.info(f"Get {len(json)} messages")

            rooms[room] = json

        return rooms

    def get_room_json(self, room: str) -> List[dict]:
        accum = []

        room = ROOT_PATH / Path(f"workspace/{room}")
        files = room.glob("*.json")

        for json_file in files:
            obj = json.load(json_file.open("r"))
            accum.extend(obj)

        return accum

    @logger.catch
    def parse_room(self, room_name: str):
        """
        Fetches the history for a room and checks all the users interactions in the room.
        Returns a dict with users and their last seen date
        :return:
        """

        # Tracked on user ID and ts
        user_last_seen: dict[str, float] = {}

        def update_if_bigger(username: str, time: float):
            if username not in user_last_seen:
                user_last_seen[username] = time
                return

            if user_last_seen[username] < time:
                user_last_seen[username] = time
                return

        messages = self.get_room_json(room_name)

        for msg in messages:

            if "user" not in msg:
                logger.debug(msg)
                continue

            poster = msg["user"]
            ts = float(msg["ts"])

            update_if_bigger(poster, ts)

            reactions = msg.get("reactions")
            if not reactions:
                continue

            for reaction in reactions:
                for user in reaction["users"]:
                    update_if_bigger(user, ts)

        return user_last_seen

    def filter_on_age(self, data: dict[str, float], cutoff_days: int):
        time_delta = datetime.timedelta(days=cutoff_days)
        cutoff_epoch = (datetime.datetime.now() - time_delta).timestamp()

        accum = {}
        for key, last_seen in data.items():
            if last_seen < cutoff_epoch:
                accum[key] = last_seen

        return accum
