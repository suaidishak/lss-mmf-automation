import json
import math
import random

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path("mmf_source")

MALAYSIA_TZ = ZoneInfo("Asia/Kuala_Lumpur")


# ============================================================
# MMF PARAMETERS
# ============================================================

PARAMETERS = {
    "humid": "%",
    "amb_temp": "C",
    "barom": "hPa",
    "ws": "m/s",
    "wd": "degree",
    "precip": "mm",
    "pvtemp": "C",
    "ghi": "W/m2",
    "north": "W/m2",
    "south": "W/m2",
    "poa": "W/m2",
    "atm": "atm",
    "tgi": "W/m2"
}


# ============================================================
# SOLAR / DAYLIGHT PROFILE
# ============================================================

def daylight_factor(timestamp):
    """
    Returns a simple solar production factor from 0.0 to 1.0.

    Sunrise  : 07:00
    Sunset   : 19:00
    Peak     : approximately 13:00
    """

    hour = (
        timestamp.hour
        + timestamp.minute / 60.0
    )

    sunrise = 7.0
    sunset = 19.0

    if hour < sunrise or hour >= sunset:
        return 0.0

    position = (
        (hour - sunrise)
        /
        (sunset - sunrise)
    )

    return max(
        0.0,
        math.sin(
            math.pi * position
        )
    )


# ============================================================
# PARAMETER GENERATION
# ============================================================

def generate_parameter_value(
    parameter,
    timestamp,
    site_factor,
    station_factor
):
    """
    Generate realistic sample values for one MMF parameter.
    """

    solar = daylight_factor(timestamp)

    # --------------------------------------------------------
    # Relative humidity
    # --------------------------------------------------------

    if parameter == "humid":

        value = (
            85
            - 30 * solar
            + random.uniform(-3, 3)
        )

        return round(
            max(0, min(100, value)),
            2
        )

    # --------------------------------------------------------
    # Ambient temperature
    # --------------------------------------------------------

    if parameter == "amb_temp":

        return round(
            25
            + 9 * solar
            + random.uniform(-1, 1),
            2
        )

    # --------------------------------------------------------
    # Barometric pressure
    # --------------------------------------------------------

    if parameter == "barom":

        return round(
            1005
            + random.uniform(-4, 4),
            2
        )

    # --------------------------------------------------------
    # Wind speed
    # --------------------------------------------------------

    if parameter == "ws":

        return round(
            max(
                0,
                1.5
                + 3.5 * solar
                + random.uniform(-1, 1)
            ),
            2
        )

    # --------------------------------------------------------
    # Wind direction
    # --------------------------------------------------------

    if parameter == "wd":

        return round(
            random.uniform(0, 360),
            2
        )

    # --------------------------------------------------------
    # Precipitation
    # --------------------------------------------------------

    if parameter == "precip":

        # Mostly dry
        if random.random() < 0.98:
            return 0.0

        return round(
            random.uniform(
                0.1,
                3.0
            ),
            2
        )

    # --------------------------------------------------------
    # PV module temperature
    # --------------------------------------------------------

    if parameter == "pvtemp":

        return round(
            26
            + 24 * solar
            + random.uniform(-2, 2),
            2
        )

    # --------------------------------------------------------
    # Global Horizontal Irradiance
    # --------------------------------------------------------

    if parameter == "ghi":

        return round(
            max(
                0,
                950
                * solar
                * site_factor
                * station_factor
                + random.uniform(-15, 15)
            ),
            2
        )

    # --------------------------------------------------------
    # North irradiance
    # --------------------------------------------------------

    if parameter == "north":

        return round(
            max(
                0,
                850
                * solar
                * site_factor
                * station_factor
                + random.uniform(-15, 15)
            ),
            2
        )

    # --------------------------------------------------------
    # South irradiance
    # --------------------------------------------------------

    if parameter == "south":

        return round(
            max(
                0,
                920
                * solar
                * site_factor
                * station_factor
                + random.uniform(-15, 15)
            ),
            2
        )

    # --------------------------------------------------------
    # Plane of Array irradiance
    # --------------------------------------------------------

    if parameter == "poa":

        return round(
            max(
                0,
                1000
                * solar
                * site_factor
                * station_factor
                + random.uniform(-20, 20)
            ),
            2
        )

    # --------------------------------------------------------
    # Atmospheric value
    # --------------------------------------------------------

    if parameter == "atm":

        return round(
            0.98
            + random.uniform(
                -0.02,
                0.02
            ),
            4
        )

    # --------------------------------------------------------
    # Total / Global irradiance style value
    # --------------------------------------------------------

    if parameter == "tgi":

        return round(
            max(
                0,
                900
                * solar
                * site_factor
                * station_factor
                + random.uniform(-15, 15)
            ),
            2
        )

    return None


# ============================================================
# GENERATE ONE WEATHER STATION
# ============================================================

def generate_station(
    site_name,
    station_name,
    output_file
):
    """
    Generate one MMF snapshot for one weather station.
    """

    now = datetime.now(
        MALAYSIA_TZ
    )

    site_number = int(
        site_name.split("-")[1]
    )

    station_number = int(
        station_name.split("-")[1]
    )

    # Small differences between sites
    site_factor = (
        0.92
        + ((site_number % 10) * 0.008)
    )

    # Small differences between stations
    station_factor = (
        0.98
        + ((station_number - 1) * 0.015)
    )

    parameters = {}

    for parameter, unit in PARAMETERS.items():

        value = generate_parameter_value(
            parameter,
            now,
            site_factor,
            station_factor
        )

        parameters[parameter] = {
            "unit": unit,
            "value": value
        }

    output = {
        "site": site_name,
        "station": station_name,
        "timestamp": now.isoformat(
            timespec="seconds"
        ),
        "timezone": "Asia/Kuala_Lumpur",
        "utc_offset": "+08:00",
        "parameters": parameters
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=========================================="
    )
    print(
        " LSS MMF SNAPSHOT GENERATOR"
    )
    print(
        "=========================================="
    )

    if not ROOT.exists():

        print()
        print(
            f"[ERROR] MMF source folder "
            f"not found: {ROOT}"
        )

        return

    generation_time = datetime.now(
        MALAYSIA_TZ
    )

    print()
    print(
        "Generation time :",
        generation_time.isoformat(
            timespec="seconds"
        )
    )

    print(
        "Timezone        : "
        "Asia/Kuala_Lumpur"
    )

    print()

    total_sites = 0
    total_stations = 0

    for site_dir in sorted(
        ROOT.iterdir()
    ):

        if not site_dir.is_dir():
            continue

        if not site_dir.name.startswith(
            "LSS-"
        ):
            continue

        total_sites += 1

        station_files = sorted(
            site_dir.glob(
                "WS-*.json"
            )
        )

        for station_file in station_files:

            station_name = (
                station_file.stem
            )

            print(
                f"[GENERATE] "
                f"{site_dir.name}/"
                f"{station_name}"
            )

            generate_station(
                site_dir.name,
                station_name,
                station_file
            )

            print(
                f"[OK] "
                f"{site_dir.name}/"
                f"{station_name}"
            )

            total_stations += 1

    print()
    print(
        "=========================================="
    )
    print(
        " MMF GENERATION COMPLETED"
    )
    print(
        "=========================================="
    )

    print(
        f"LSS sites generated      : "
        f"{total_sites}"
    )

    print(
        f"Weather stations generated: "
        f"{total_stations}"
    )

    print(
        f"Output directory          : "
        f"{ROOT.resolve()}"
    )

    print(
        "=========================================="
    )


if __name__ == "__main__":
    main()