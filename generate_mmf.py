import json
import math
import random

from datetime import datetime
from pathlib import Path


ROOT = Path("mmf_source")

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


def daylight_factor(timestamp):

    hour = timestamp.hour + timestamp.minute / 60.0

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
        math.sin(math.pi * position)
    )


def generate_parameter_value(
    parameter,
    timestamp,
    site_factor,
    station_factor
):

    solar = daylight_factor(timestamp)

    if parameter == "humid":
        return round(
            85 - 30 * solar + random.uniform(-3, 3),
            2
        )

    if parameter == "amb_temp":
        return round(
            25 + 9 * solar + random.uniform(-1, 1),
            2
        )

    if parameter == "barom":
        return round(
            1005 + random.uniform(-4, 4),
            2
        )

    if parameter == "ws":
        return round(
            max(
                0,
                1.5 + 3.5 * solar + random.uniform(-1, 1)
            ),
            2
        )

    if parameter == "wd":
        return round(
            random.uniform(0, 360),
            2
        )

    if parameter == "precip":

        if random.random() < 0.98:
            return 0.0

        return round(
            random.uniform(0.1, 3.0),
            2
        )

    if parameter == "pvtemp":
        return round(
            26 + 24 * solar + random.uniform(-2, 2),
            2
        )

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

    if parameter == "atm":
        return round(
            0.98 + random.uniform(-0.02, 0.02),
            4
        )

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


def generate_station(
    site_name,
    station_name,
    output_file
):

    now = datetime.now()

    site_number = int(
        site_name.split("-")[1]
    )

    station_number = int(
        station_name.split("-")[1]
    )

    site_factor = (
        0.92
        + ((site_number % 10) * 0.008)
    )

    station_factor = (
        0.98
        + ((station_number - 1) * 0.015)
    )

    parameters = {}

    for parameter, unit in PARAMETERS.items():

        parameters[parameter] = {
            "unit": unit,
            "value": generate_parameter_value(
                parameter,
                now,
                site_factor,
                station_factor
            )
        }

    output = {
        "site": site_name,
        "station": station_name,
        "timestamp": now.isoformat(timespec="seconds"),
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


def main():

    print("==========================================")
    print(" LSS MMF SNAPSHOT GENERATOR")
    print("==========================================")

    if not ROOT.exists():

        print(f"[ERROR] Folder not found: {ROOT}")
        return

    total = 0

    for site_dir in sorted(ROOT.iterdir()):

        if not site_dir.is_dir():
            continue

        if not site_dir.name.startswith("LSS-"):
            continue

        for station_file in sorted(
            site_dir.glob("WS-*.json")
        ):

            station_name = station_file.stem

            print(
                f"[GENERATE] "
                f"{site_dir.name}/{station_name}"
            )

            generate_station(
                site_dir.name,
                station_name,
                station_file
            )

            total += 1

    print("")
    print("==========================================")
    print(f"Weather stations generated: {total}")
    print("==========================================")


if __name__ == "__main__":
    main()
