#!/usr/bin/env python3

import typer

app = typer.Typer()


@app.command()
def cleanup(
    live: bool = typer.Option(
        True,
        help="Set this flag when you are ready to trigger the changes instead of just testing",
    ),
):
    pass


if __name__ == "__main__":
    app()
