"""Tests for GUI input helpers."""

from __future__ import annotations

import pytest

from weather_cli.gui import WeatherGuiInputError, parse_coordinate_input


def test_parse_coordinate_input_returns_float() -> None:
    assert parse_coordinate_input("Latitude", " 51.5072 ") == 51.5072


def test_parse_coordinate_input_rejects_empty_value() -> None:
    with pytest.raises(WeatherGuiInputError, match="Latitude is required"):
        parse_coordinate_input("Latitude", "   ")


def test_parse_coordinate_input_rejects_non_numeric_value() -> None:
    with pytest.raises(WeatherGuiInputError, match="Longitude must be a number"):
        parse_coordinate_input("Longitude", "west")
