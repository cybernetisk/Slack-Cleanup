#!/usr/bin/env python3
from typing import List
import yaml
from helpers import ROOT_PATH

from pydantic import BaseModel


class Testing(BaseModel):
    user_msg: str
    user_test: str


class Channels(BaseModel):
    testing: str
    logging: str
    adding: List[str]
    cleanup: List[str]


# This file parses out the config and passes it as a dataclass
class Config(BaseModel):
    timeout: int
    testing: Testing
    channels: Channels
    message: str


class AuthClient(BaseModel):
    id: str
    secret: str


class Auth(BaseModel):
    app_id: str
    client: AuthClient
    token: str


def _get_auth() -> Auth:
    f = (ROOT_PATH / "auth.yaml").open("r")
    y = yaml.safe_load(f)
    return Auth.parse_obj(y)


def _get_config() -> Config:
    f = (ROOT_PATH / "config.yaml").open("r")
    y = yaml.safe_load(f)
    return Config.parse_obj(y)


config = _get_config()
auth = _get_auth()
