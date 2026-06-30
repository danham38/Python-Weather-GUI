"""Custom exceptions and validation helpers for the weather CLI."""

from __future__ import annotations


class WeatherCliError(Exception):
    """Base exception for expected CLI failures."""

    error_code = "WEATHER_CLI_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.message} ({self.error_code})"


class CoordinateValidationError(WeatherCliError):
    """Base exception for invalid coordinate input."""

    error_code = "INVALID_COORDINATE"

    def __init__(self, coordinate_name: str, value: float, minimum: float, maximum: float) -> None:
        self.coordinate_name = coordinate_name
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(
            f"Invalid {coordinate_name}: {value}. Expected a value between {minimum} and {maximum}."
        )


class LatitudeValidationError(CoordinateValidationError):
    """Raised when latitude is outside the valid range."""

    error_code = "INVALID_LATITUDE"

    def __init__(self, value: float) -> None:
        super().__init__("latitude", value, -90, 90)


class LongitudeValidationError(CoordinateValidationError):
    """Raised when longitude is outside the valid range."""

    error_code = "INVALID_LONGITUDE"

    def __init__(self, value: float) -> None:
        super().__init__("longitude", value, -180, 180)


class WeatherProviderError(WeatherCliError):
    """Base exception for weather provider failures."""

    error_code = "WEATHER_PROVIDER_ERROR"


class WeatherProviderTimeoutError(WeatherProviderError):
    """Raised when the weather provider times out."""

    error_code = "WEATHER_PROVIDER_TIMEOUT"


class WeatherProviderConnectionError(WeatherProviderError):
    """Raised when the weather provider cannot be reached."""

    error_code = "WEATHER_PROVIDER_CONNECTION_ERROR"


class WeatherProviderStatusError(WeatherProviderError):
    """Raised when the weather provider returns a bad HTTP status."""

    error_code = "WEATHER_PROVIDER_BAD_STATUS"

    def __init__(self, status_code: int, response_text: str = "") -> None:
        self.status_code = status_code
        self.response_text = response_text
        detail = f"Weather provider returned status {status_code}."
        if response_text:
            detail += f" Response: {response_text[:200]}"
        super().__init__(detail)


class WeatherProviderResponseError(WeatherProviderError):
    """Raised when the weather provider returns malformed or incomplete data."""

    error_code = "WEATHER_PROVIDER_BAD_RESPONSE"


def validate_latitude(latitude: float) -> float:
    """Validate and return latitude.

    Valid latitude is inclusive: -90 <= latitude <= 90.
    """

    if latitude < -90 or latitude > 90:
        raise LatitudeValidationError(latitude)
    return latitude


def validate_longitude(longitude: float) -> float:
    """Validate and return longitude.

    Valid longitude is inclusive: -180 <= longitude <= 180.
    """

    if longitude < -180 or longitude > 180:
        raise LongitudeValidationError(longitude)
    return longitude


def validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    """Validate latitude and longitude together."""

    return validate_latitude(latitude), validate_longitude(longitude)
