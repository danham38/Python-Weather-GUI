from weather_cli.formatting.terminal_formatter import format_weather_report
from weather_cli.models import WeatherReport


def test_format_weather_report_includes_core_fields():
    report = WeatherReport(
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

    output = format_weather_report(report)

    assert "Current weather" in output
    assert "51.5072, -0.1276" in output
    assert "Mainly clear" in output
    assert "21.5°C" in output
    assert "From cache: no" in output
