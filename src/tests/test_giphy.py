# coding=utf-8
import pytest
from copy import deepcopy

from flack.message import PrivateResponse

from .. import giphy


# https://developers.giphy.com/docs/api/endpoint#search
SEARCH_DATA = [
    {
        "url": "http://giphy.com/gifs/confused-flying-YsTs5ltWtEhnq",
        "embed_url": "http://giphy.com/embed/YsTs5ltWtEhnq",
        "source_tld": "cheezburger.com",
        "rating": "pg-13",
        "title": "Happy Dancing GIF",
        "user": {
            "display_name": "CoolDude"
        },
        "images": {
            "original": {
                "url": "https://media2.giphy.com/media/abc123/giphy.gif",
                "mp4": "https://media2.giphy.com/media/abc123/giphy.mp4",
                "webp": "https://media2.giphy.com/media/abc123/giphy.webp"
            },
            "hd": {
                "mp4": "https://media2.giphy.com/media/abc123/giphy-hd.mp4",
                "webp": "https://media2.giphy.com/media/abc123/giphy-hd.webp"
            }
        }
    }
]


def test_gif_search(requests_mock):
    # Bad response
    requests_mock.get("http://api.giphy.com/v1/gifs/search", status_code=403)
    result = giphy.gif_search("test")
    assert isinstance(result, PrivateResponse)
    assert "error" in result.feedback

    # Empty response
    requests_mock.get("http://api.giphy.com/v1/gifs/search", json={})
    result = giphy.gif_search("test")
    assert isinstance(result, PrivateResponse)
    assert "No matches" in result.feedback

    # Good responses
    requests_mock.get(
        "http://api.giphy.com/v1/gifs/search",
        json={"data": SEARCH_DATA}
    )
    result = giphy.gif_search("test")
    assert result.indirect.image_url == "https://media2.giphy.com/media/abc123/giphy-hd.mp4"
    assert result.indirect.title == "Happy Dancing GIF"
    assert "pg-13" in result.indirect.text
    assert "CoolDude" in result.indirect.text
    assert "cheezburger.com" in result.indirect.text


def test__get_image_url():
    images = deepcopy(SEARCH_DATA[0]["images"])

    # HD > Original, MP4 > WEBP > GIF
    assert giphy._get_image_url(images) == "https://media2.giphy.com/media/abc123/giphy-hd.mp4"
    images["hd"].pop("mp4")
    assert giphy._get_image_url(images) == "https://media2.giphy.com/media/abc123/giphy-hd.webp"
    images["hd"].pop("webp")
    assert giphy._get_image_url(images) == "https://media2.giphy.com/media/abc123/giphy.mp4"
    images["original"].pop("mp4")
    assert giphy._get_image_url(images) == "https://media2.giphy.com/media/abc123/giphy.webp"
    images["original"].pop("webp")
    assert giphy._get_image_url(images) == "https://media2.giphy.com/media/abc123/giphy.gif"

    images["original"].pop("url")
    with pytest.raises(KeyError):
        giphy._get_image_url(images)
