#!/usr/bin/env python3


import typer
from loguru import logger

import helpers
import slack_api
from cfg import auth, config
from export import Export


app = typer.Typer()


@app.command()
def cleanup(
    live: bool = typer.Option(
        False,
        help="Set this flag when you are ready to trigger the changes instead of just testing",
    ),
):
    """
    Runs the cleanup script for our slack.

    Checks the list <channels.cleanup> for users that has been inactive for at least
    <timeout> number of days. That is, no reactions or posts/replies.

    When they are removed they are also sent a message <message> and added to the group <channels.adding>

    :param live: Denotes if this is a dry run or a real run
    :return: None
    """

    logger.info(f"Running cleanup! Live: {live}")

    api = slack_api.Api(token=auth.token, live=live)
    export = Export()

    for channel in api.convo_cleanup():
        logger.info(f"Checking {channel['name']}")

        timestamps = export.parse_room(channel["name"])
        users_filtered = export.filter_on_age(timestamps, config.timeout)

        logger.info(f"Found {len(timestamps.keys())} users")
        logger.info(f"{len(users_filtered.keys())}")

        for user_id, timestamp in users_filtered.items():
            username = helpers.convert_id_to_name(user_id)
            date = helpers.convert_epoch_to_date(timestamp)

            # DM user
            api.msg_user_config_message(user_id)

            # Remove from channel
            logger.info(
                f"Removing from {channel['name']}: {username}, last seen {date}"
            )
            api.user_remove(channel_id=channel["id"], user_id=user_id)

            # Adding to channel
            for channel_add in api.convo_adding():
                api.user_add(channel_id=channel_add["id"], user_id=user_id)


if __name__ == "__main__":
    app()
