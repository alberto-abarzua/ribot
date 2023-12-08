import logging
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "cyan",
        "status": "white",
        "move_tool": "yellow",
        "move_joints": "green",
        "move_angles": "green",
        "set_tool": "blue",
        "set_settings": "purple",
        "homing": "bold green",
        "waiting": "bold red",
        "big_info": "bold green_yellow",
        "important": "bold green",
        "warning": "magenta",
        "error": "bold red",
        "danger": "bold red",
        "light_info": "dim white",
        "setup": "bold dodger_blue1",
        "success": "bold green",
    }
)


console_original = Console(theme=custom_theme, force_terminal=True, width=150)
console = console_original
console_original_file = console.file


class NullDevice:
    def write(self, _: str) -> None:
        pass

    def flush(self) -> None:
        pass


def _disable_console() -> None:
    console.file = NullDevice()  # type: ignore


def _enable_console() -> None:
    console.file = console_original_file


def global_disble_console() -> None:
    console.file = NullDevice()  # type: ignore


def disable_console(func: Callable) -> Callable:
    def inner(*args: Tuple[int, str], **kwargs: Dict[str, Any]) -> Any:
        _disable_console()
        res = func(*args, **kwargs)
        _enable_console()
        return res

    return inner


def set_log_file(file: Path) -> None:
    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=False, console=console)],
    )
    console.file = open(file, "a")


def reset_console_file() -> None:
    if console.file:
        console.file.close()
    console.file = console_original_file
