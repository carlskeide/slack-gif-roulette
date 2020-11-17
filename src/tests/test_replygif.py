# coding=utf-8
import pytest
from unittest.mock import patch

from flack.message import PrivateResponse

from .. import app, replygif


# http://replygif.net/about
TAGS = [
    {
        "title": "agreeing",
        "id": "95",
        "reaction": True,
        "url": "http://replygif.net/t/agreeing",
        "reply": "Yes",
        "count": "21"
    },
    {
        "title": "nod",
        "id": "83",
        "reaction": True,
        "url": "http://replygif.net/t/nod",
        "reply": "Yes",
        "count": "39"
    }
]

GIFS = [
    {
        "id": "1401",
        "tags":
            [
                "okay",
                "right",
                "George Costanza",
                "Seinfeld"
            ],
        "caption": [],
        "url": "http://replygif.net/1401",
        "file": "http://replygif.net/i/1401.gif"
    },
    {
        "id": "392",
        "tags":
            [
                "okay",
                "right",
                "Seinfeld"
            ],
        "caption": [],
        "url": "http://replygif.net/392",
        "file": "http://replygif.net/i/392.gif"
    }
]


def setup_module():
    app.config["TESTING"] = True
    app.config["CACHE_TYPE"] = "simple"
    replygif.cache.init_app(app)


def test_get_tags(requests_mock):
    with app.app_context():
        replygif.cache.clear()

    requests_mock.get("http://replygif.net/api/tags", status_code=403)
    with pytest.raises(Exception):
        replygif.get_tags()

    requests_mock.get("http://replygif.net/api/tags", json=TAGS)
    tags = replygif.get_tags()
    assert tags == {"agreeing", "nod"}


def test_fuzzy_match():
    with patch.object(replygif, "get_tags") as mocked:
        mocked.return_value = ["agreeing", "nod", "kitten"]

        matched_tags = replygif.fuzzy_match(["agree", "kiten"])
        assert matched_tags == ["agreeing", "kitten"]

        with pytest.raises(Exception) as e:
            replygif.fuzzy_match(["not"])
        assert "did you mean: nod" in str(e.value)


def test_gif_search(requests_mock):
    with patch.object(replygif, "fuzzy_match") as mocked:
        mocked.return_value = ["okay", "right"]

        # Bad response
        requests_mock.get("http://replygif.net/api/gifs", status_code=403)
        result = replygif.gif_search(["test", ])
        assert isinstance(result, PrivateResponse)
        assert "error" in result.feedback

        # Empty response
        requests_mock.get("http://replygif.net/api/gifs", json={})
        result = replygif.gif_search(["test", ])
        assert isinstance(result, PrivateResponse)
        assert "No matches" in result.feedback

        # Good responses
        requests_mock.get("http://replygif.net/api/gifs", json=GIFS)
        result = replygif.gif_search(["test", ])
        assert result.indirect.image_url in [gif["file"] for gif in GIFS]

        requests_mock.get("http://replygif.net/api/gifs", json=[GIFS[0], ])
        result = replygif.gif_search(["test", ])
        assert result.indirect.image_url == "http://replygif.net/i/1401.gif"
        assert "#1401" in result.indirect.title
        assert "George Costanza" in result.indirect.text
