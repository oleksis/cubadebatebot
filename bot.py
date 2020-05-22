#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys

# Import GitHub Workspace for runner of GitHub Actions
GH_WORKSPACE = os.getenv("GITHUB_WORKSPACE")
sys.path.insert(0, GH_WORKSPACE)

import requests
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors.common import MultiError

from conf.telegram import (
    TG_API_ID,
    TG_API_HASH,
    TG_TOKEN,
    TG_AUTHORIZATION,
    TG_CHANNEL,
    TG_BOT,
)

ConnectionErrorRequests = requests.exceptions.ConnectionError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# client = TelegramClient(TG_SESSION, TG_API_ID, TG_API_HASH)
client = TelegramClient(StringSession(TG_AUTHORIZATION), TG_API_ID, TG_API_HASH)


async def main(link: str):
    """Entry point"""
    try:
        # Telegram API get all message channel. You need id of Channel
        channel_id = -1001279889036
        channel_entity = await client.get_input_entity(channel_id)
        channel = await client.get_entity(channel_entity)

        urls = set()
        # By day we public 3 messages then we get the last 10 by default
        async for msg in client.iter_messages(channel, 10):
            if msg.media and msg.media.webpage:
                _url = msg.media.webpage.url
                urls.add(_url)

        if link not in urls:
            # Client is me, is my bot, send my message :)
            _ = await client.send_message(TG_BOT, link)
            # Send message to the Channel with my Bot [^_^]
            bot = await client.start(bot_token=TG_TOKEN)
            update = await bot.send_message(TG_CHANNEL, link)
            logger.info(f"Bot Telegram sending message: {update.message}")
    except MultiError as error:
        logger.error(error)


if __name__ == "__main__":
    # TODO: capture the msg_link from external workflow
    # msg_link = sys.argv[1]
    msg_link = ""
    try:
        url = "https://oleksis.github.io/cubadebate/top_word_post.json"
        data = requests.get(url).json()
        msg_link = list(data["url"].values())[0]
    except ConnectionErrorRequests:
        pass  # Try again! Occurred Connection Error

    if msg_link:
        with client:
            # authorization_key = client.session.save()
            # print(authorization_key)
            client.loop.run_until_complete(main(msg_link))
