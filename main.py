#!/usr/bin/env python3

import typer
from config import config

app = typer.Typer()
from slack_api import Api


@app.command()
def test_msg():
    api = Api()
    channels = api.conversations()
    pass


@app.command()
def cleanup(
    dry: bool = typer.Option(False),
):
    pass


if __name__ == "__main__":
    app()
