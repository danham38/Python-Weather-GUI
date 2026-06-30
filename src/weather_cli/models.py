"""Data models used by the weather CLI."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class WeatherReport:
    """Current weather data for one coordinate pair."""

    latitude: float
    longitude: float
    timezone: str
    observation_time: str
    temperature: float
    apparent_temperature: float | None
    temperature_unit: str
    relative_humidity: int | None
    humidity_unit: str
    precipitation: float | None
    precipitation_unit: str
    weather_code: int | None
    wind_speed: float | None
    wind_speed_unit: str
    wind_direction: int | None
    wind_direction_unit: str
    source: str = "Open-Meteo"
    from_cache: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert report to a JSON-serialisable dictionary."""

        return asdict(self)

    def mark_from_cache(self) -> "WeatherReport":
        """Return a copy of the report marked as coming from cache."""

        data = self.to_dict()
        data["from_cache"] = True
        return WeatherReport(**data)
