import os
import time
import requests

from pathlib import Path


USERNAME = "suaidishak"

API_TOKEN = os.environ.get(
    "PYTHONANYWHERE_API_TOKEN"
)

LOCAL_ROOT = Path("mmf_source")

REMOTE_ROOT = (
    "/home/suaidishak/mysite/mmf_sites"
)

MAX_RETRIES = 5
RETRY_DELAY = 5
UPLOAD_DELAY = 0.5


session = requests.Session()


def configure_session():

    if not API_TOKEN:

        raise RuntimeError(
            "PYTHONANYWHERE_API_TOKEN "
            "environment variable is not set."
        )

    session.headers.update({
        "Authorization": f"Token {API_TOKEN}"
    })


def upload_file(
    local_file,
    remote_file
):

    url = (
        f"https://www.pythonanywhere.com"
        f"/api/v0/user/{USERNAME}"
        f"/files/path{remote_file}"
    )

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            with open(
                local_file,
                "rb"
            ) as f:

                response = session.post(
                    url,
                    files={"content": f},
                    timeout=60
                )

            if response.status_code in (
                200,
                201
            ):

                return True

            print(
                f"    HTTP {response.status_code}"
            )

        except requests.exceptions.RequestException as e:

            print(
                f"    Upload error: {e}"
            )

        if attempt < MAX_RETRIES:

            time.sleep(
                RETRY_DELAY
            )

    return False


def main():

    configure_session()

    print("==========================================")
    print(" LSS MMF UPLOADER")
    print("==========================================")

    successful = 0
    failed = 0

    for site_dir in sorted(
        LOCAL_ROOT.iterdir()
    ):

        if not site_dir.is_dir():
            continue

        if not site_dir.name.startswith(
            "LSS-"
        ):
            continue

        print("")
        print(site_dir.name)

        for station_file in sorted(
            site_dir.glob(
                "WS-*.json"
            )
        ):

            remote_file = (
                f"{REMOTE_ROOT}/"
                f"{site_dir.name}/"
                f"{station_file.name}"
            )

            print(
                f"  Uploading "
                f"{station_file.name}"
            )

            if upload_file(
                station_file,
                remote_file
            ):

                print(
                    "    [OK]"
                )

                successful += 1

            else:

                print(
                    "    [FAILED]"
                )

                failed += 1

            time.sleep(
                UPLOAD_DELAY
            )

    print("")
    print("==========================================")
    print(" MMF UPLOAD SUMMARY")
    print("==========================================")
    print(f"Successful : {successful}")
    print(f"Failed     : {failed}")
    print("==========================================")


if __name__ == "__main__":
    main()
