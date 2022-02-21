#!/usr/bin/env python3

# https://typer.tiangolo.com/tutorial/testing/
# https://docs.pytest.org/en/6.2.x/fixture.html

from typer.testing import CliRunner

from main import app

runner = CliRunner()


def test_msg():
    res = runner.invoke(app, ["test_msg"])
    print(res)
