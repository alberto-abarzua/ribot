# mypy: ignore-errors
import os
from typing import Any

import requests  # type: ignore # noqa: F401
from packaging import version


def get_version(*args: Any, **kwargs: Any) -> str:
    url = "https://pypi.org/pypi/ribot-controller/json"

    override_version = os.getenv("PDM_OVERRIDE_VERSION", "")

    if "none" in override_version.lower():
        override_version = None

    if override_version is not None:
        return override_version

    response = requests.get(url)
    if response.status_code == 200:
        package_info = response.json()
        current_version_str = package_info["info"]["version"]

        # Parse the version string
        current_version = version.parse(current_version_str)
        print(f"Current version: {current_version}")

        # Increment the minor version
        new_version = version.Version(f"{current_version.major}.{current_version.minor}.{current_version.micro+1}")

        return str(new_version)
    else:
        raise Exception("Failed to retrieve package information")
