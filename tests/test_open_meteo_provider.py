import pytest
import requests

from weather_cli.errors import (
    WeatherProviderConnectionError,
    WeatherProviderResponseError,
    WeatherProviderStatusError,
    WeatherProviderTimeoutError,
)
from weather_cli.providers.open_meteo import OpenMeteoProvider


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def valid_payload():
    return {
        "latitude": 51.5,
        "longitude": -0.12,
        "timezone": "Europe/London",
        "current_units": {
            "temperature_2m": "°C",
            "relative_humidity_2m": "%",
            "precipitation": "mm",
            "wind_speed_10m": "km/h",
            "wind_direction_10m": "°",
        },
        "current": {
            "time": "2026-06-30T12:00",
            "temperature_2m": 21.5,
            "relative_humidity_2m": 55,
            "apparent_temperature": 20.7,
            "precipitation": 0,
            "weather_code": 1,
            "wind_speed_10m": 12.3,
            "wind_direction_10m": 180,
        },
    }


def test_open_meteo_provider_parses_valid_response(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse(payload=valid_payload())

    monkeypatch.setattr(requests, "get", fake_get)

    provider = OpenMeteoProvider()
    report = provider.get_current_weather(51.5072, -0.1276)

    assert report.temperature == 21.5
    assert report.timezone == "Europe/London"
    assert report.weather_code == 1


def test_open_meteo_provider_raises_on_timeout(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "get", fake_get)

    provider = OpenMeteoProvider()
    with pytest.raises(WeatherProviderTimeoutError):
        provider.get_current_weather(51.5072, -0.1276)


def test_open_meteo_provider_raises_on_connection_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError()

    monkeypatch.setattr(requests, "get", fake_get)

    provider = OpenMeteoProvider()
    with pytest.raises(WeatherProviderConnectionError):
        provider.get_current_weather(51.5072, -0.1276)


def test_open_meteo_provider_raises_on_bad_status(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse(status_code=500, payload={}, text="server error")

    monkeypatch.setattr(requests, "get", fake_get)

    provider = OpenMeteoProvider()
    with pytest.raises(WeatherProviderStatusError):
        provider.get_current_weather(51.5072, -0.1276)


def test_open_meteo_provider_raises_on_bad_json(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse(payload=ValueError("bad json"))

    monkeypatch.setattr(requests, "get", fake_get)

    provider = OpenMeteoProvider()
    with pytest.raises(WeatherProviderResponseError):
        provider.get_current_weather(51.5072, -0.1276)


def test_open_meteo_provider_raises_when_current_block_missing():
    provider = OpenMeteoProvider()

    with pytest.raises(WeatherProviderResponseError):
        provider._parse_weather_response({"latitude": 51.5, "longitude": -0.12})
