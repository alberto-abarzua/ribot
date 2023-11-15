# mypy: ignore-errors
import os
from typing import Any

import requests  # type: ignore
from packaging import version


def get_version(*args: Any, **kwargs: Any) -> str:
    url = "https://pypi.org/pypi/ribot-controller/json"

    override_version = os.getenv("PDM_OVERRIDE_VERSION", "")
    increment_version = os.getenv("PDM_INCREMENT_VERSION", "false")

    if override_version != "" and "none" not in override_version.lower():
        return override_version

    response = requests.get(url)

    if response.status_code == 200:
        package_info = response.json()
        current_version_str = package_info["info"]["version"]

        # Parse the version string
        current_version = version.parse(current_version_str)

        # Increment the minor version
        if increment_version.lower() == "true":
            new_version = version.Version(f"{current_version.major}.{current_version.minor}.{current_version.micro + 1}")
        else:
            new_version = version.Version(f"{current_version.major}.{current_version.minor}.{current_version.micro}")

        return str(new_version)

    return "0.0.0"
