import argparse

from weather_cli.cli import build_parser


def test_cli_parser_accepts_required_coordinates():
    parser = build_parser()
    args = parser.parse_args(["--lat", "51.5072", "--lon", "-0.1276"])

    assert isinstance(args, argparse.Namespace)
    assert args.lat == 51.5072
    assert args.lon == -0.1276
    assert args.units == "celsius"
    assert args.no_cache is False


def test_cli_parser_accepts_json_and_no_cache_flags():
    parser = build_parser()
    args = parser.parse_args(["--lat", "51.5072", "--lon", "-0.1276", "--json", "--no-cache"])

    assert args.json is True
    assert args.no_cache is True
