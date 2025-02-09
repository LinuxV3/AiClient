import os, sys
from logger import log
from gui import run_gui
from cli import run_cli


def is_gui_running():
    """
    This function checks if the GUI is running by checking enviroment variable. (actually detect if the user interface is GUI or not)
    """
    return 'DISPLAY' in os.environ


def get_desktop_environment():
    """
    This function detect and return the user`s desktop environment by checking the enviroment variable.
    """
    return os.environ.get('XDG_CURRENT_DESKTOP', False)


args = [arg.lower() for arg in sys.argv]
is_gui = is_gui_running()
desktop_env = get_desktop_environment()
if is_gui or '--gui' in args or '-g' in args:
    log(f"Your current desktop environment is: {desktop_env}", "INFO")
    log("running application in GUI interface...", "INFO")
    run_gui()
else:
    log("You are running on a headless interface", "INFO")
    log("the CLI version of AiClient app is comming soon...", "INFO")
    log("If you are using a GUI interface just use --gui argument")
