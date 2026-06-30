"""Provider interface for weather data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod

from weather_cli.models import WeatherReport


class WeatherProvider(ABC):
    """Abstract interface for weather providers."""

    @abstractmethod
    def get_current_weather(self, latitude: float, longitude: float) -> WeatherReport:
        """Return current weather for a coordinate pair."""
