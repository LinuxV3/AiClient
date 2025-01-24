import os
from logger import log
from gui import run_gui
from cli import run_cli


def is_gui_running():
    return 'DISPLAY' in os.environ


def get_desktop_environment():
    return os.environ.get('XDG_CURRENT_DESKTOP', False)


is_gui = is_gui_running()
desktop_env = get_desktop_environment()
if is_gui:
    log(f"Your current desktop environment is: {desktop_env}", "INFO")
    log("Using GUI to run application.", "INFO")
    run_gui()
else:
    log("You are running on a headless interface", "INFO")
    log("So We start CLI application", "INFO")
    run_cli()

