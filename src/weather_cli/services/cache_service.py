"""Simple JSON file cache for weather responses."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from weather_cli.models import WeatherReport


class CacheService:
    """TTL-based cache backed by a JSON file."""

    def __init__(self, cache_path: Path | None = None, ttl_seconds: int = 900) -> None:
        self.cache_path = cache_path or Path.home() / ".weather_cli" / "cache.json"
        self.ttl_seconds = ttl_seconds

    def get(self, key: str) -> WeatherReport | None:
        """Return a fresh cached report, or None if missing or expired."""

        cache = self._read_cache()
        item = cache.get(key)
        if not item:
            return None

        timestamp = item.get("timestamp")
        report_data = item.get("report")
        if not isinstance(timestamp, (int, float)) or not isinstance(report_data, dict):
            return None

        if time.time() - timestamp > self.ttl_seconds:
            return None

        try:
            return WeatherReport(**report_data).mark_from_cache()
        except TypeError:
            return None

    def set(self, key: str, report: WeatherReport) -> None:
        """Store a weather report in the cache."""

        cache = self._read_cache()
        report_data = report.to_dict()
        report_data["from_cache"] = False
        cache[key] = {
            "timestamp": time.time(),
            "report": report_data,
        }
        self._write_cache(cache)

    def _read_cache(self) -> dict[str, Any]:
        if not self.cache_path.exists():
            return {}
        try:
            with self.cache_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def _write_cache(self, cache: dict[str, Any]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_path.open("w", encoding="utf-8") as file:
            json.dump(cache, file, indent=2)
