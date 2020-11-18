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
                "height": "187",
                "width": "245",
                "size": "730871",
                "url": "https://media4.giphy.com/media/qmfpjpAT2fJRK/giphy.gif",
                "mp4_size": "1068619",
                "mp4": "https://media4.giphy.com/media/qmfpjpAT2fJRK/giphy.mp4",
                "webp_size": "438512",
                "webp": "https://media4.giphy.com/media/qmfpjpAT2fJRK/giphy.webp",
                "frames": "34",
                "hash": "47e1fcca22164e408fc980c4d5691069"
            },
            "downsized_large": {
                "height": "187",
                "width": "245",
                "size": "730871",
                "url": "https://media4.giphy.com/media/qmfpjpAT2fJRK/giphy.gif"
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
    assert result.indirect.image_url == "https://media4.giphy.com/media/qmfpjpAT2fJRK/giphy.gif"
    assert result.indirect.title == "Happy Dancing GIF"
    assert "pg-13" in result.indirect.text
    assert "CoolDude" in result.indirect.text
    assert "cheezburger.com" in result.indirect.text


def test__get_image_url():
    images = deepcopy(SEARCH_DATA[0]["images"])

    assert giphy._get_image_url(images) == "https://media4.giphy.com/media/qmfpjpAT2fJRK/giphy.gif"

    images.pop("downsized_large")
    assert giphy._get_image_url(images) == "https://media4.giphy.com/media/qmfpjpAT2fJRK/giphy.gif"

    images["original"].pop("url")
    with pytest.raises(KeyError):
        giphy._get_image_url(images)
