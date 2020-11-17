# coding=utf-8
import logging
import random
import html

from flack.message import Attachment, IndirectResponse, PrivateResponse

from requests import get
from fuzzywuzzy import process

from . import config, cache

logger = logging.getLogger(__name__)


@cache.cached(timeout=3600, key_prefix='replygif_tags')
def get_tags():
    logger.info("Fetching tags from replygif")
    try:
        params = {"api-key": config.REPLYGIF_API_KEY}
        if config.REPLYGIF_ONLY_REPLYTAGS:
            params.update(reaction=1)

        response = get("http://replygif.net/api/tags", params=params)
        replygif_tags = {tag["title"] for tag in response.json()}
        logger.debug("Got %d tags", len(replygif_tags))

    except Exception:
        logger.exception("Bad response from API")
        raise Exception("API error, please try again later")

    else:
        return replygif_tags


def fuzzy_match(raw_tags):
    logger.info("Attempting to match tags: %s", raw_tags)
    replygif_tags = get_tags()
    matched_tags = []

    for raw_tag in raw_tags:
        logger.debug("fuzzing tag: {}".format(raw_tag))

        fuzzy = process.extract(raw_tag, replygif_tags, limit=3)
        logger.debug("fuzzy result: {!r}".format(fuzzy))

        if fuzzy[0][1] >= config.REPLYGIF_TAG_MATCH_ACC:
            matched_tags.append(fuzzy[0][0])

        else:
            alternatives = ["{} ({}%)".format(f[0], f[1]) for f in fuzzy]
            raise Exception(
                "No good match for: '{}', did you mean: {}".format(
                    raw_tag, ", ".join(alternatives)))

    return matched_tags


def gif_search(tags):
    try:
        matched_tags = fuzzy_match(tags)

    except Exception as e:
        return PrivateResponse(str(e))

    logger.info("Searching ReplyGif for tags: %s", matched_tags)
    try:
        response = get("http://replygif.net/api/gifs", {
            "api-key": config.REPLYGIF_API_KEY,
            "tag-operator": "and",
            "tag": ",".join(matched_tags)
        })
        response.raise_for_status()
        results = response.json()

    except Exception:
        logger.exception("Bad response from API: %r", response)
        return PrivateResponse("API error, please try again later")

    try:
        replygif = random.choice(results)

    except IndexError:
        return PrivateResponse("No matches for tags: {}".format(matched_tags))

    logger.info("Selected %s (from %d items)", replygif["url"], len(results))
    title = "#{}".format(replygif["id"])
    if replygif["caption"]:
        title += ": {}".format(replygif["caption"])

    return IndirectResponse(
        feedback=True,  # Echo command invokation to channel
        indirect=Attachment(
            title=html.unescape(title),
            title_link=replygif["url"],
            fallback=title,
            text=html.unescape(", ".join(replygif["tags"])),
            image_url=replygif["file"]))
