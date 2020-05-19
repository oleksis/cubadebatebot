#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os, sys

# Import GitHub Workspace for runner of GitHub Actions
GH_WORKSPACE = os.getenv("GITHUB_WORKSPACE")
sys.path.insert(0, GH_WORKSPACE)

import requests
from telegram import Bot
from telegram.error import TelegramError

from conf.telegram import TLG_API_KEY, TLG_CHANNEL


ConnectionErrorRequests = requests.exceptions.ConnectionError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main(text: str, token: str):
    bot_telegram = Bot(token=token)
    try:
        message = bot_telegram.send_message(chat_id=TLG_CHANNEL, text=text)
        logger.info(f"Bot Telegram sending message: {message.text_html}")
    except TelegramError as error:
        logger.error(error)


if __name__ == "__main__":
    # TODO: capture the msg from external workflow
    # msg = sys.argv[1]
    msg = ""
    try:
        url = "https://oleksis.github.io/cubadebate/top_word_post.json"
        data = requests.get(url).json()
        link = list(data["url"].values())[0]
        msg = link
    except ConnectionErrorRequests:
        pass  # Try again! Occurred Connection Error

    if msg:
        main(msg, TLG_API_KEY)
