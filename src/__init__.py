# coding=utf-8
import logging

from flask import Flask
from flask_caching import Cache
from flack import Flack
from flack.message import PrivateResponse

from . import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(config)

flack = Flack(app)

cache = Cache(app)

# Avoids circular dependency by importing after app/redis are defined
from . import giphy, replygif  # noqa


@flack.command("/giphy")
def command_giphy(text, **kwargs):
    if not text:
        return PrivateResponse("Usage: `/giphy *search_string*`")

    return giphy.gif_search(text)


@flack.command("/replygif")
def command_replygif(text, **kwargs):
    tags = [s.strip() for s in text.split(",")]
    if not tags[0]:
        return PrivateResponse(
            "Usage: `/replygif *tag* [, *tag2*, *tag3*, ...]`")

    return replygif.gif_search(tags)
