"""Tests for ask_info tool."""

import json
from unittest.mock import patch

import pytest

from hallw.tools.ask_info import ask_for_more_info


def test_ask_for_more_info_success():
    """Test asking for more info with user input."""
    with patch("builtins.input", return_value="User response here"):
        result = ask_for_more_info.invoke({"question": "What is your name?"})
        data = json.loads(result)

        assert data["success"] is True
        assert "User provided additional information" in data["message"]
        assert data["data"]["response"] == "User response here"


def test_ask_for_more_info_empty_response():
    """Test asking for more info with empty user input."""
    with patch("builtins.input", return_value=""):
        result = ask_for_more_info.invoke({"question": "What is your name?"})
        data = json.loads(result)

        assert data["success"] is True
        assert data["data"]["response"] == ""
