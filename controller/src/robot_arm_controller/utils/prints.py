from typing import Any, Callable, Dict, Tuple

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "dim green_yellow",
        "big_info": "bold green_yellow",
        "important": "bold green",
        "warning": "magenta",
        "error": "bold red",
        "danger": "bold red",
        "light_info": "dim white",
        "note": "bold blue",
        "setup": "bold dodger_blue1",
        "success": "bold green",
    }
)


console_original = Console(theme=custom_theme, force_terminal=True)
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


def disable_console(func: Callable) -> Callable:
    def inner(*args: Tuple[int, str], **kwargs: Dict[str, Any]) -> Any:
        _disable_console()
        res = func(*args, **kwargs)
        _enable_console()
        return res

    return inner
