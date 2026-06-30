"""Tkinter desktop GUI for the weather app."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import ttk

from weather_cli.errors import WeatherCliError
from weather_cli.formatting.terminal_formatter import format_weather_report
from weather_cli.providers.open_meteo import OpenMeteoProvider
from weather_cli.services.cache_service import CacheService
from weather_cli.services.weather_service import WeatherService


class WeatherGuiInputError(ValueError):
    """Raised when GUI input cannot be parsed before domain validation."""


def parse_coordinate_input(name: str, raw_value: str) -> float:
    """Parse a coordinate text box value into a float.

    Domain validation still happens in WeatherService. This helper only checks
    that the text box contains something numeric.
    """

    cleaned_value = raw_value.strip()
    if not cleaned_value:
        raise WeatherGuiInputError(f"{name} is required.")

    try:
        return float(cleaned_value)
    except ValueError as exc:
        raise WeatherGuiInputError(f"{name} must be a number.") from exc


class WeatherGuiApp:
    """Small Tkinter application for fetching current weather."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Weather CLI GUI")
        self.root.minsize(560, 520)

        self.latitude_var = tk.StringVar(value="51.5072")
        self.longitude_var = tk.StringVar(value="-0.1276")
        self.units_var = tk.StringVar(value="celsius")
        self.use_cache_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Enter coordinates and fetch the current weather.")

        self._result_queue: queue.Queue[tuple[str, str]] = queue.Queue()

        self._build_layout()
        self.root.after(100, self._poll_result_queue)

    def _build_layout(self) -> None:
        main_frame = ttk.Frame(self.root, padding=18)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(main_frame, text="Weather Lookup", font=("TkDefaultFont", 18, "bold"))
        title.pack(anchor=tk.W, pady=(0, 14))

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X)

        ttk.Label(form_frame, text="Latitude").grid(row=0, column=0, sticky=tk.W, pady=6)
        latitude_entry = ttk.Entry(form_frame, textvariable=self.latitude_var, width=22)
        latitude_entry.grid(row=0, column=1, sticky=tk.EW, padx=(12, 0), pady=6)

        ttk.Label(form_frame, text="Longitude").grid(row=1, column=0, sticky=tk.W, pady=6)
        longitude_entry = ttk.Entry(form_frame, textvariable=self.longitude_var, width=22)
        longitude_entry.grid(row=1, column=1, sticky=tk.EW, padx=(12, 0), pady=6)

        ttk.Label(form_frame, text="Units").grid(row=2, column=0, sticky=tk.W, pady=6)
        units_combo = ttk.Combobox(
            form_frame,
            textvariable=self.units_var,
            values=("celsius", "fahrenheit"),
            state="readonly",
            width=19,
        )
        units_combo.grid(row=2, column=1, sticky=tk.EW, padx=(12, 0), pady=6)

        cache_checkbox = ttk.Checkbutton(
            form_frame,
            text="Use cache",
            variable=self.use_cache_var,
        )
        cache_checkbox.grid(row=3, column=1, sticky=tk.W, padx=(12, 0), pady=6)

        form_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(12, 10))

        self.fetch_button = ttk.Button(button_frame, text="Fetch weather", command=self.fetch_weather)
        self.fetch_button.pack(side=tk.LEFT)

        london_button = ttk.Button(button_frame, text="London", command=self._set_london_coordinates)
        london_button.pack(side=tk.LEFT, padx=(8, 0))

        clear_button = ttk.Button(button_frame, text="Clear", command=self._clear_output)
        clear_button.pack(side=tk.LEFT, padx=(8, 0))

        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W, pady=(2, 8))

        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=16, state=tk.DISABLED)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.configure(yscrollcommand=scrollbar.set)

        latitude_entry.focus_set()

    def _set_london_coordinates(self) -> None:
        self.latitude_var.set("51.5072")
        self.longitude_var.set("-0.1276")

    def _clear_output(self) -> None:
        self.status_var.set("Output cleared.")
        self._write_output("")

    def fetch_weather(self) -> None:
        """Start a weather lookup without blocking the GUI event loop."""

        try:
            latitude = parse_coordinate_input("Latitude", self.latitude_var.get())
            longitude = parse_coordinate_input("Longitude", self.longitude_var.get())
        except WeatherGuiInputError as exc:
            self.status_var.set("Input error.")
            self._write_output(f"Error: {exc}")
            return

        self.fetch_button.configure(state=tk.DISABLED)
        self.status_var.set("Fetching weather...")
        self._write_output("Fetching weather...")

        worker = threading.Thread(
            target=self._fetch_weather_in_background,
            args=(latitude, longitude, self.units_var.get(), self.use_cache_var.get()),
            daemon=True,
        )
        worker.start()

    def _fetch_weather_in_background(
        self,
        latitude: float,
        longitude: float,
        units: str,
        use_cache: bool,
    ) -> None:
        provider = OpenMeteoProvider(timeout_seconds=10.0, temperature_unit=units)
        cache_service = CacheService(ttl_seconds=15 * 60)
        weather_service = WeatherService(provider=provider, cache_service=cache_service)

        try:
            report = weather_service.get_current_weather(
                latitude=latitude,
                longitude=longitude,
                use_cache=use_cache,
            )
        except WeatherCliError as exc:
            self._result_queue.put(("error", f"Error: {exc}"))
            return
        except Exception as exc:  # pragma: no cover - final GUI safety net
            self._result_queue.put(("error", f"Unexpected error: {exc}"))
            return

        self._result_queue.put(("success", format_weather_report(report)))

    def _poll_result_queue(self) -> None:
        try:
            status, message = self._result_queue.get_nowait()
        except queue.Empty:
            self.root.after(100, self._poll_result_queue)
            return

        if status == "success":
            self.status_var.set("Weather fetched successfully.")
        else:
            self.status_var.set("Weather lookup failed.")

        self.fetch_button.configure(state=tk.NORMAL)
        self._write_output(message)
        self.root.after(100, self._poll_result_queue)

    def _write_output(self, value: str) -> None:
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        if value:
            self.output_text.insert(tk.END, value)
        self.output_text.configure(state=tk.DISABLED)


def main() -> None:
    """Start the GUI application."""

    root = tk.Tk()
    app = WeatherGuiApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
