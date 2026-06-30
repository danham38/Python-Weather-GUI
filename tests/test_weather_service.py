import pytest

from weather_cli.errors import LatitudeValidationError
from weather_cli.models import WeatherReport
from weather_cli.providers.base import WeatherProvider
from weather_cli.services.cache_service import CacheService
from weather_cli.services.weather_service import WeatherService


class FakeProvider(WeatherProvider):
    def __init__(self) -> None:
        self.call_count = 0

    def get_current_weather(self, latitude: float, longitude: float) -> WeatherReport:
        self.call_count += 1
        return WeatherReport(
            latitude=latitude,
            longitude=longitude,
            timezone="Europe/London",
            observation_time="2026-06-30T12:00",
            temperature=21.5,
            apparent_temperature=20.7,
            temperature_unit="°C",
            relative_humidity=55,
            humidity_unit="%",
            precipitation=0.0,
            precipitation_unit="mm",
            weather_code=1,
            wind_speed=12.3,
            wind_speed_unit="km/h",
            wind_direction=180,
            wind_direction_unit="°",
        )


def test_weather_service_validates_coordinates_before_provider_call(tmp_path):
    provider = FakeProvider()
    service = WeatherService(provider=provider, cache_service=CacheService(tmp_path / "cache.json"))

    with pytest.raises(LatitudeValidationError):
        service.get_current_weather(999, 0)

    assert provider.call_count == 0


def test_weather_service_uses_provider_then_cache(tmp_path):
    provider = FakeProvider()
    service = WeatherService(provider=provider, cache_service=CacheService(tmp_path / "cache.json"))

    first = service.get_current_weather(51.5072, -0.1276)
    second = service.get_current_weather(51.5072, -0.1276)

    assert first.from_cache is False
    assert second.from_cache is True
    assert provider.call_count == 1


def test_weather_service_bypasses_cache_when_disabled(tmp_path):
    provider = FakeProvider()
    service = WeatherService(provider=provider, cache_service=CacheService(tmp_path / "cache.json"))

    service.get_current_weather(51.5072, -0.1276, use_cache=False)
    service.get_current_weather(51.5072, -0.1276, use_cache=False)

    assert provider.call_count == 2
