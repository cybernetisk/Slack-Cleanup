#!/usr/bin/env python3

import typer

app = typer.Typer()


@app.command
def test_msg(
    token: str = typer.Argument(None, envvar="SLACK_TOKEN"),
):
    pass


@app.command
def cleanup(
    token: str = typer.Argument(None, envvar="SLACK_TOKEN"),
    dry: bool = typer.Option(False),
):
    pass


if __name__ == "__main__":
    app()
