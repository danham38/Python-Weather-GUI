"""Application service for the weather CLI."""

from __future__ import annotations

from weather_cli.errors import validate_coordinates
from weather_cli.models import WeatherReport
from weather_cli.providers.base import WeatherProvider
from weather_cli.services.cache_service import CacheService


class WeatherService:
    """Coordinates validation, caching, and provider access."""

    def __init__(self, provider: WeatherProvider, cache_service: CacheService | None = None) -> None:
        self.provider = provider
        self.cache_service = cache_service

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        use_cache: bool = True,
    ) -> WeatherReport:
        """Return current weather, using cache when enabled and fresh."""

        valid_latitude, valid_longitude = validate_coordinates(latitude, longitude)
        cache_key = self._cache_key(valid_latitude, valid_longitude)

        if use_cache and self.cache_service is not None:
            cached_report = self.cache_service.get(cache_key)
            if cached_report is not None:
                return cached_report

        report = self.provider.get_current_weather(valid_latitude, valid_longitude)

        if use_cache and self.cache_service is not None:
            self.cache_service.set(cache_key, report)

        return report

    @staticmethod
    def _cache_key(latitude: float, longitude: float) -> str:
        """Build a stable cache key for coordinates."""

        return f"lat={latitude:.4f};lon={longitude:.4f}"
