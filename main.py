import os, sys, platform, core
core.configure_app()
from PyQt5.QtWidgets import QMainWindow
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
os_name = platform.system().lower()
desktop_env = 'Windows' if os_name == 'windows' else get_desktop_environment()
if '--help' in args or '-h' in args:
    print(f'Usage:   {sys.executable} [options]', end='\n\n\n')
    print(f'Options: ')
    print(f'            --service [service_name]: Run a specific service, Services are image[ImageGenerator], translator[Translator]')
    print(f"            --help: Print this help message and exit")
    print(f"            --gui: force application to run in GUI interface", end='\n\n\n')
    exit()

if '--service' in args:
    service_name = args[args.index('--service') + 1].lower()
    if service_name in ['translator', 't', 'translate']:
        log("Running Translator service...", "INFO")
        try:
            from plugins.Translator.app import TranslatorApp
            translator_window = QMainWindow()
            translator_app = TranslatorApp()
            translator_app.setupUi(translator_window)
            translator_window.show()
        except Exception as error:
            log(f"Error in running translator: {error}", 'error')
    elif service_name in ['imagegenerator', 'i', 'ig', 'image', 'image_generator']:
        log("Running ImageGenerator service...", "INFO")
        try:
            from plugins.ImageGenerator.app import ImageGeneratorApp
            image_generator_app = ImageGeneratorApp()
            image_generator_app.show()
        except Exception as error:
            log(f"Error in running image generator: {error}", 'error')
    else:
        log("Unknown Service, We just have translator and ImageGenerator services.", "INFO")
        exit()
    exit()
if is_gui or '--gui' in args or '-g' in args or os_name == 'windows':
    log(f"Your current desktop environment is: {desktop_env}", "INFO")
    log("running application in GUI interface...", "INFO")
    run_gui()
else:
    log("You are running on a headless interface", "INFO")
    log("the CLI version of AiClient app is comming soon...", "INFO")
    log("If you are using a GUI interface just use --gui argument")
