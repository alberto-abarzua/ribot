from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "dim green_yellow",
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
    def write(self, s):
        pass

    def flush(self):
        pass


def _disable_console():
    console.file = NullDevice()


def _enable_console():
    console.file = console_original_file





def disable_console(func):
    def inner(*args, **kwargs):
        _disable_console()
        res = func(*args, **kwargs)
        _enable_console()
        return res

    return inner


