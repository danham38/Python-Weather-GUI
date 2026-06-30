"""Terminal output formatting for weather reports."""

from __future__ import annotations

from weather_cli.formatting.weather_codes import describe_weather_code
from weather_cli.models import WeatherReport


def format_optional_value(value: object, unit: str = "") -> str:
    """Format an optional value for display."""

    if value is None:
        return "N/A"
    return f"{value}{unit}"


def format_weather_report(report: WeatherReport) -> str:
    """Format a weather report as a readable terminal string."""

    cache_note = "yes" if report.from_cache else "no"
    condition = describe_weather_code(report.weather_code)

    lines = [
        "Current weather",
        "---------------",
        f"Location: {report.latitude:.4f}, {report.longitude:.4f}",
        f"Timezone: {report.timezone}",
        f"Observation time: {report.observation_time}",
        f"Condition: {condition}",
        f"Temperature: {report.temperature}{report.temperature_unit}",
        f"Feels like: {format_optional_value(report.apparent_temperature, report.temperature_unit)}",
        f"Humidity: {format_optional_value(report.relative_humidity, report.humidity_unit)}",
        f"Precipitation: {format_optional_value(report.precipitation, report.precipitation_unit)}",
        f"Wind: {format_optional_value(report.wind_speed, report.wind_speed_unit)}",
        f"Wind direction: {format_optional_value(report.wind_direction, report.wind_direction_unit)}",
        f"Source: {report.source}",
        f"From cache: {cache_note}",
    ]
    return "\n".join(lines)
