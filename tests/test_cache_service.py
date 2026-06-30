import json
import time

from weather_cli.models import WeatherReport
from weather_cli.services.cache_service import CacheService


def make_report() -> WeatherReport:
    return WeatherReport(
        latitude=51.5072,
        longitude=-0.1276,
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


def test_cache_service_stores_and_reads_fresh_report(tmp_path):
    cache_path = tmp_path / "cache.json"
    cache = CacheService(cache_path=cache_path, ttl_seconds=60)

    cache.set("london", make_report())
    report = cache.get("london")

    assert report is not None
    assert report.temperature == 21.5
    assert report.from_cache is True


def test_cache_service_returns_none_for_expired_report(tmp_path):
    cache_path = tmp_path / "cache.json"
    report = make_report().to_dict()
    cache_path.write_text(
        json.dumps({"london": {"timestamp": time.time() - 120, "report": report}}),
        encoding="utf-8",
    )

    cache = CacheService(cache_path=cache_path, ttl_seconds=60)

    assert cache.get("london") is None


def test_cache_service_ignores_invalid_json(tmp_path):
    cache_path = tmp_path / "cache.json"
    cache_path.write_text("not-json", encoding="utf-8")

    cache = CacheService(cache_path=cache_path, ttl_seconds=60)

    assert cache.get("london") is None
