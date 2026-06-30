"""Open-Meteo provider implementation."""

from __future__ import annotations

from typing import Any

import requests

from weather_cli.errors import (
    WeatherProviderConnectionError,
    WeatherProviderResponseError,
    WeatherProviderStatusError,
    WeatherProviderTimeoutError,
)
from weather_cli.models import WeatherReport
from weather_cli.providers.base import WeatherProvider


class OpenMeteoProvider(WeatherProvider):
    """Fetches current weather from the Open-Meteo forecast API."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout_seconds: float = 10.0, temperature_unit: str = "celsius") -> None:
        self.timeout_seconds = timeout_seconds
        if temperature_unit not in {"celsius", "fahrenheit"}:
            raise ValueError("temperature_unit must be 'celsius' or 'fahrenheit'")
        self.temperature_unit = temperature_unit

    def get_current_weather(self, latitude: float, longitude: float) -> WeatherReport:
        """Fetch and parse current weather data."""

        payload = self._request_weather(latitude, longitude)
        return self._parse_weather_response(payload)

    def _request_weather(self, latitude: float, longitude: float) -> dict[str, Any]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m",
                ]
            ),
            "timezone": "auto",
            "temperature_unit": self.temperature_unit,
            "forecast_days": 1,
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=self.timeout_seconds)
        except requests.Timeout as exc:
            raise WeatherProviderTimeoutError("Weather provider request timed out.") from exc
        except requests.RequestException as exc:
            raise WeatherProviderConnectionError("Could not connect to the weather provider.") from exc

        if not 200 <= response.status_code < 300:
            raise WeatherProviderStatusError(response.status_code, response.text)

        try:
            payload = response.json()
        except ValueError as exc:
            raise WeatherProviderResponseError("Weather provider returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise WeatherProviderResponseError("Weather provider returned an unexpected response shape.")

        return payload

    @staticmethod
    def _parse_weather_response(payload: dict[str, Any]) -> WeatherReport:
        current = payload.get("current")
        current_units = payload.get("current_units", {})

        if not isinstance(current, dict):
            raise WeatherProviderResponseError("Weather provider response is missing the current weather block.")
        if "temperature_2m" not in current:
            raise WeatherProviderResponseError("Weather provider response is missing current temperature.")
        if "time" not in current:
            raise WeatherProviderResponseError("Weather provider response is missing observation time.")

        try:
            latitude = float(payload["latitude"])
            longitude = float(payload["longitude"])
        except (KeyError, TypeError, ValueError) as exc:
            raise WeatherProviderResponseError("Weather provider response is missing coordinates.") from exc

        return WeatherReport(
            latitude=latitude,
            longitude=longitude,
            timezone=str(payload.get("timezone", "unknown")),
            observation_time=str(current["time"]),
            temperature=current["temperature_2m"],
            apparent_temperature=current.get("apparent_temperature"),
            temperature_unit=str(current_units.get("temperature_2m", "")),
            relative_humidity=current.get("relative_humidity_2m"),
            humidity_unit=str(current_units.get("relative_humidity_2m", "")),
            precipitation=current.get("precipitation"),
            precipitation_unit=str(current_units.get("precipitation", "")),
            weather_code=current.get("weather_code"),
            wind_speed=current.get("wind_speed_10m"),
            wind_speed_unit=str(current_units.get("wind_speed_10m", "")),
            wind_direction=current.get("wind_direction_10m"),
            wind_direction_unit=str(current_units.get("wind_direction_10m", "")),
        )
