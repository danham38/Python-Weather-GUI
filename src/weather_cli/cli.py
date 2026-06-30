"""Command-line entry point for the weather CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from weather_cli.errors import WeatherCliError
from weather_cli.formatting.terminal_formatter import format_weather_report
from weather_cli.providers.open_meteo import OpenMeteoProvider
from weather_cli.services.cache_service import CacheService
from weather_cli.services.weather_service import WeatherService


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="weather-cli",
        description="Fetch current weather for a latitude and longitude.",
    )
    parser.add_argument("--lat", type=float, required=True, help="Latitude, from -90 to 90.")
    parser.add_argument("--lon", type=float, required=True, help="Longitude, from -180 to 180.")
    parser.add_argument(
        "--units",
        choices=["celsius", "fahrenheit"],
        default="celsius",
        help="Temperature unit to request from the provider. Default: celsius.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="API timeout in seconds. Default: 10.",
    )
    parser.add_argument(
        "--cache-ttl-minutes",
        type=int,
        default=15,
        help="Cache time-to-live in minutes. Default: 15.",
    )
    parser.add_argument(
        "--cache-path",
        type=Path,
        default=None,
        help="Optional custom cache file path.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable reading from and writing to the cache.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the weather report as JSON.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    """Execute the CLI command and return a process exit code."""

    provider = OpenMeteoProvider(timeout_seconds=args.timeout, temperature_unit=args.units)
    cache_service = CacheService(
        cache_path=args.cache_path,
        ttl_seconds=args.cache_ttl_minutes * 60,
    )
    weather_service = WeatherService(provider=provider, cache_service=cache_service)

    try:
        report = weather_service.get_current_weather(
            latitude=args.lat,
            longitude=args.lon,
            use_cache=not args.no_cache,
        )
    except WeatherCliError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(format_weather_report(report))

    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
