import pytest

from weather_cli.errors import (
    LatitudeValidationError,
    LongitudeValidationError,
    validate_coordinates,
    validate_latitude,
    validate_longitude,
)


def test_validate_latitude_accepts_boundary_values():
    assert validate_latitude(-90) == -90
    assert validate_latitude(90) == 90


def test_validate_latitude_rejects_values_outside_range():
    with pytest.raises(LatitudeValidationError):
        validate_latitude(-90.1)

    with pytest.raises(LatitudeValidationError):
        validate_latitude(90.1)


def test_validate_longitude_accepts_boundary_values():
    assert validate_longitude(-180) == -180
    assert validate_longitude(180) == 180


def test_validate_longitude_rejects_values_outside_range():
    with pytest.raises(LongitudeValidationError):
        validate_longitude(-180.1)

    with pytest.raises(LongitudeValidationError):
        validate_longitude(180.1)


def test_validate_coordinates_returns_valid_pair():
    assert validate_coordinates(51.5, -0.12) == (51.5, -0.12)
