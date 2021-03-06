#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import os
import re
import sys

# Import GitHub Workspace for runner of GitHub Actions
GH_WORKSPACE = os.getenv("GITHUB_WORKSPACE")
sys.path.insert(0, GH_WORKSPACE)

import requests
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaWebPage
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


def in_24_hours(link: str):
    """Link generated in 24 hours"""

    def extract_date(str_link):
        """Extract date from link URL return str or None"""
        str_date = None
        pattern = r"(?P<date>\d{4}/\d{2}/\d{2})"
        link_date_group = re.search(pattern, str_link)
        if link_date_group:
            str_date = link_date_group.group("date")
        return str_date

    date_str = extract_date(link)

    if not date_str:
        return False

    link_date = datetime.strptime(date_str, "%Y/%m/%d")
    today = datetime.now()
    days = (today - link_date).days

    return days <= 1


# client = TelegramClient(TG_SESSION, TG_API_ID, TG_API_HASH)
client = TelegramClient(StringSession(TG_AUTHORIZATION), TG_API_ID, TG_API_HASH)


async def main(links: list):
    """Entry point"""
    try:
        # Telegram API get all message channel. You need id of Channel
        channel_id = -1001279889036
        channel_entity = await client.get_input_entity(channel_id)
        channel = await client.get_entity(channel_entity)

        urls = set()
        # By day we public 3 messages then we get the last 20 by default
        async for msg in client.iter_messages(channel, limit=20):
            if (
                hasattr(msg, "media")
                and isinstance(msg.media, MessageMediaWebPage)
                and hasattr(msg.media.webpage, "url")
            ):
                _url = msg.media.webpage.url
                urls.add(_url)

        links2send = []

        for link in links:
            if link not in urls:
                if in_24_hours(link):
                    links2send.append(link)
                else:
                    # The links comes in order
                    break

        for link in reversed(links2send):
            # I'm the Client (me), is my bot, send my message :)
            _ = await client.send_message(TG_BOT, link)
            # Send message to the Channel with my Bot [^_^]
            bot = await client.start(bot_token=TG_TOKEN)
            update = await bot.send_message(TG_CHANNEL, link)
            logger.info(f"Bot Telegram sending message: {update.message}")
    except MultiError as error:
        logger.error(error)


if __name__ == "__main__":
    # TODO: capture the msg_links from external workflow
    # msg_links = sys.argv[1]
    msg_links = None
    try:
        url = "https://oleksis.github.io/cubadebate/top_word_post.json"
        data = requests.get(url).json()
        msg_links = list(data["url"].values())
    except ConnectionErrorRequests:
        pass  # Try again! Occurred Connection Error

    if msg_links:
        with client:
            # authorization_key = client.session.save()
            # print(authorization_key)
            client.loop.run_until_complete(main(msg_links))
