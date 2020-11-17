# coding=utf-8
import logging
import random
import html

from flack.message import Attachment, IndirectResponse, PrivateResponse

from requests import get

from . import config

logger = logging.getLogger(__name__)


def _get_image_url(images):
    try:
        image_url = images["hd"].get("mp4") or images["hd"]["webp"]
        logger.debug("Selected HD image: %s", image_url)
        return image_url

    except KeyError:
        logger.warning("Unable to get HD version")

    image_url = (
        images["original"].get("mp4")
        or images["original"].get("webp")
        or images["original"]["url"]
    )

    logger.debug("Selected original image: %s", image_url)
    return image_url


def gif_search(search_string):
    logger.info("Searching Giphy for: %s", search_string)

    param = {
        "api_key": config.GIPHY_API_KEY,
        "rating": config.GIPHY_RATING,
        "limit": config.GIPHY_POOL,
        "q": search_string
    }

    try:
        response = get("http://api.giphy.com/v1/gifs/search", param)
        response.raise_for_status()
        results = response.json().get('data', [])

    except Exception:
        logger.exception("Bad response from API")
        return PrivateResponse("API error, please try again later")

    try:
        selected = random.choice(results)

    except IndexError:
        return PrivateResponse("No matches for: {}".format(search_string))

    logger.info("Selected %s (from %d items)", selected["url"], len(results))

    try:
        image_url = _get_image_url(selected["images"])

    except Exception:
        logger.exception("Unable to extract image url")
        return PrivateResponse("API error, please try again later")

    title = selected.get("title", "_gif_")
    user = selected.get("user", {})

    info = []
    if user.get("display_name"):
        info.append("Via: {}".format(user["display_name"]))

    if selected.get("source_tld"):
        info.append("Source: {}".format(selected["source_tld"]))

    if "rating" in selected:
        info.append("[{}]".format(selected["rating"]))

    return IndirectResponse(
        feedback=True,  # Echo command invokation to channel
        indirect=Attachment(
            title=html.unescape(title),
            title_link=selected["url"],
            fallback=title,
            text=html.unescape(", ".join(info)),
            image_url=image_url))
