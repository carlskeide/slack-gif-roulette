# coding=utf-8
from unittest.mock import patch

from .. import command_giphy, command_replygif
from .. import replygif, giphy


def test_command_giphy():
    response = command_giphy("")
    assert "Usage" in response.feedback

    with patch.object(giphy, "gif_search") as mock_search:
        mock_search.return_value = "baz.gif"
        response = command_giphy("foobar")

        mock_search.assert_called_with("foobar")
        assert response == "baz.gif"


def test_command_replygif():
    response = command_replygif("")
    assert "Usage" in response.feedback

    with patch.object(replygif, "gif_search") as mock_search:
        mock_search.return_value = "baz.gif"

        response = command_replygif("foo")
        mock_search.assert_called_with(["foo"])
        assert response == "baz.gif"

        response = command_replygif("foo, bar ,baz ")
        mock_search.assert_called_with(["foo", "bar", "baz"])
