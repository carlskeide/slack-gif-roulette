# coding=utf-8
import sec

LOG_LEVEL = sec.load("log_level", fallback="INFO").upper()

# Flask
DEBUG = False

# Flask-Caching
CACHE_TYPE = "redis"
CACHE_REDIS_URL = sec.load("redis_url", fallback="redis://localhost")
CACHE_DEFAULT_TIMEOUT = 600

# Flack
FLACK_URL_PREFIX = "/"
FLACK_DEFAULT_NAME = "GifRoulette"
FLACK_TOKEN = sec.load("slack_token")

# App
GIPHY_API_KEY = sec.load("giphy_key")

GIPHY_RATING = "pg-13"
GIPHY_POOL = 16

REPLYGIF_API_KEY = sec.load("replygif_key")

REPLYGIF_ONLY_REPLYTAGS = False
REPLYGIF_TAG_MATCH_ACC = 90
REPLYGIF_TAG_CACHE_LEN = (60 * 60 * 24 * 7)
