from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "dim green_yellow",
        "important": "bold green",
        "warning": "magenta",
        "danger": "bold red",
        "light_info": "dim white",
        "note": "bold blue",
        "setup": "bold dodger_blue1",
    }
)


console = Console(theme=custom_theme,force_terminal=True)
