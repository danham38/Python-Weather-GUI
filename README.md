# Weather CLI Project

A Python command-line weather tool that validates coordinates, fetches current weather from the Open-Meteo API, formats the result, and caches recent responses.

## Features

- Accepts latitude and longitude from the terminal.
- Validates latitude in `[-90, 90]` and longitude in `[-180, 180]`.
- Fetches current weather from Open-Meteo.
- Handles bad API status codes, timeouts, network errors, and malformed API responses.
- Caches successful responses to avoid unnecessary API calls.
- Supports text output and JSON output.
- Includes unit tests for validation, caching, formatting, service logic, provider behaviour, and GUI input parsing.
- Provides both a terminal CLI and a small Tkinter desktop GUI.

## Project structure

```text
weather_cli_project/
├── pyproject.toml
├── requirements.txt
├── README.md
├── REQUIREMENTS.md
├── src/
│   └── weather_cli/
│       ├── __init__.py
│       ├── cli.py
│       ├── errors.py
│       ├── gui.py
│       ├── models.py
│       ├── formatting/
│       │   ├── __init__.py
│       │   ├── terminal_formatter.py
│       │   └── weather_codes.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── open_meteo.py
│       └── services/
│           ├── __init__.py
│           ├── cache_service.py
│           └── weather_service.py
└── tests/
    ├── test_cache_service.py
    ├── test_cli.py
    ├── test_errors.py
    ├── test_gui.py
    ├── test_open_meteo_provider.py
    ├── test_terminal_formatter.py
    └── test_weather_service.py
```

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Run the CLI

```bash
weather-cli --lat 51.5072 --lon -0.1276
```

Or without installing the console command:

```bash
PYTHONPATH=src python -m weather_cli.cli --lat 51.5072 --lon -0.1276
```


## Run the GUI

After setup, launch the desktop app with:

```bash
weather-gui
```

Or run it directly without installing the console command:

```bash
PYTHONPATH=src python -m weather_cli.gui
```

The GUI uses Tkinter, which is included with most standard Python installs on macOS. If your Python installation does not include Tkinter, install a Python distribution that includes Tcl/Tk support.

## JSON output

```bash
weather-cli --lat 51.5072 --lon -0.1276 --json
```

## Disable cache

```bash
weather-cli --lat 51.5072 --lon -0.1276 --no-cache
```

## Run tests

```bash
pytest
```


