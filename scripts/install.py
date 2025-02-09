import os, sys, shutil, platform, subprocess, importlib
import logging

install_packages = False

try:
    from git import Repo  # pip install gitpython
    from tqdm import tqdm
    import requests
except ImportError:
    install_packages = True


log_format = '%(asctime)s -> %(levelname)s: %(message)s' # For example '2022-07-09 14:30:00,123 -> INFO: This is a test'
date_format = '%Y-%m-%d %H:%M:%S'
logger = logging.getLogger("AiClient")
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format)
log_types = {"debug": logger.debug,
             "info": logger.info,
             "error": logger.error,
             "critical": logger.critical,
             'warning': logger.warning,
             'warn': logger.warning,
             'log': logger.log}


def download_file(url, save_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    with open(save_path, 'wb') as file:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=save_path) as bar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                bar.update(len(data))


def is_package_installed(package_name):
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name, interperter=None, req_file=None):
    if not interperter:
        interperter = sys.executable
    if req_file:
        package_name = req_file
    if not is_package_installed(package_name):
        try:
            if req_file:
                subprocess.check_call([interperter, "-m", "pip", "install", '-r', package_name])
            else:
                subprocess.check_call([interperter, "-m", "pip", "install", package_name])
            print(f"Successfully installed {package_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package_name}. Error: {e}")
    else:
        print(f"{package_name} is already installed.")


def log(dest: str, log_type='INFO') -> None:
    log_type = log_type.lower()
    if log_type in log_types:
        log_types[log_type](dest)
    else:
        logger.debug(dest)


def activate_venv(venv_name="venv"):
    if os.name == "nt":
        activate_script = os.path.join(venv_name, "Scripts", "activate")
    else:
        activate_script = os.path.join(venv_name, "bin", "activate")

    print(f"Virtual environment created. To activate it, run:")
    print(f"source {activate_script}" if os.name != "nt" else f"{activate_script}")

    if os.name == "nt":
        subprocess.run([activate_script], shell=True)
    else:
        subprocess.run(f"source {activate_script}", shell=True, executable="/bin/bash")


def add_alias_to_bashrc(alias_name, alias_command):
    bashrc_path = os.path.expanduser("~/.bashrc")
    alias_line = f'alias {alias_name}="{alias_command}"\n'
    with open(bashrc_path, "r") as bashrc_file:
        if alias_line in bashrc_file.read():
            return False
    
    with open(bashrc_path, "a") as bashrc_file:
        bashrc_file.write(alias_line)
    return True


def is_debian_based():
    try:
        with open("/etc/os-release", "r") as f:
            os_release = f.read()
        return "debian" in os_release.lower() or "ubuntu" in os_release.lower()
    except FileNotFoundError:
        return False


if install_packages:
    packages = {"git": 'gitpython', 'requests': 'requests', 'tqdm': 'tqdm'}
    for package in list(packages.keys()):
        if not is_package_installed(package):
            log(f"`{package}` not installed. Installing `{package}`...")
            install_package(packages[package])
            if is_package_installed(package):
                log(f"`{package}` installed successfully.")
            else:
                log(f"`{package}` not installed!", 'error')
                log(f"Install it then try again.", 'info')
                log("If you see any `externally-managed-environment` error, Follow bellow steps:", 'info')
                log(f"First install virtualenv using `{sys.executable} pip install virtualenv`", 'info')
                log(f"now you have to create a virtualenv using `{sys.executable} -m venv installenv`", 'info')
                log(f"Then you need to activate the virtualenv using `source installenv/bin/activate` in Linux or `installenv/Scripts/activate` in Windows", 'info')
                log(f"Then you can run this script using `{sys.executable}` install.py")
                exit()
    try:
        from git import Repo  # pip install gitpython
        from tqdm import tqdm
        import requests
    except ImportError as err:
        log(f"Error in import moudle: {err}", 'error')
        exit()


args = [arg.lower() for arg in sys.argv]
python_versions = ['3.12.3']
python_versions_str = ', '.join(python_versions)
install_dir = os.path.realpath(os.path.expanduser("~"))
git_url = "https://github.com/linuxv3/AiClient"
windows_installer_file = "https://raw.github.usercontent.com/linuxv3/AiClient/scripts/AiClient4Win.msi"
repo_dir = "./AiClient"
os_name = platform.system().lower()
pythonv = platform.python_version()
skip_dl = '--skip-download' in args or '--skip-dl' in args
use_source_code = False
given_os = False
if '--use-source-code' in args:
    os_name = 'linux'
    use_source_code = True
    ignore_shortcut = True
for arg in args:
    if arg.startswith("--os"):
        os_name = args[args.index(arg) + 1].replace("--os", '')
        os_name = os_name.replace(" ", '')
        os_name = os_name.lower()
        given_os = True
        break
just_help = '--help' in args or '-h' in args
just_info = '--info' in args or '-i' in args
if just_help:
    print(f"Usage: {sys.executable} install.py [options]", end='\n\n\n')
    print("Options:")
    print("         `--help` Print this help and exit.")
    print("         `--info` Print your system info, the app info and exit.")
    print("         `--os YOUR_OS_NAME` give you os name manually")
    print("         `--install-python x.y.z` Install python x.y.z version. for example `--install-python 3.12.3`")
    print("         `--use-source-code` build and download the app from the git repository.")
    print("         `--skip-download` [use along `--use-source-code` option] Use this option when you cloned the repository and want to skip downloading the repository.")
    print("\n\n\n")
if just_info:
    print("         OS:", os_name)
    print("         Python version:", pythonv)
    print(f"         Supported python versions: {python_versions_str}")
    print(f"         Install directory: {install_dir}")
    print("         App repository:", git_url)
    print("\n\n\n")
if just_help or just_info:
    exit()


if use_source_code and given_os:
    log("You can`t use `--os` and `--use-source-code` options together", 'error')
    exit()


if '--install-python' in args:
    print("Use InstallPython.sh script for install python")
    exit()


if (os_name == 'windows' or os_name == 'win') and not use_source_code:
    log("You are using Windows, cool", 'info')
    log("Downloading app installer for Windows...", 'info')
    try:
        save_path = os.path.join(install_dir, 'installer')
        os.makedirs(save_path, exist_ok=True)
        save_path = os.path.join(save_path, windows_installer_file.split("/")[-1])
        download_file(windows_installer_file, save_path)
    except Exception as e:
        log("Error in downloading installer: " + str(e), 'error')
        log("Download the installer manually from " + windows_installer_file, 'info')
        exit()
    else:
        log("App installer downloaded successfully and saved at " + save_path, 'info')
        log("Starting the installer...", 'info')
        try:
            os.open(save_path)
        except Exception as err:
            log(f"Error in launching installer: {err}")
            log(f"Launch it manually from {windows_installer_file}")
            exit()
        else:
            log("Good luck")
            log("Thanks for downloading the App")
            exit()
    exit()


if use_source_code:
    if pythonv not in python_versions:
        log("the App does not support your python version, use --info option for see supported python versions", 'warn')
        log("But maybe it work", 'info')
    if not skip_dl:
        try:
            Repo.clone_from(git_url, repo_dir)
        except Exception as e:
            log("Error clonning repository: " + str(e), "error")
            log("Clone the repository in AiClient folder then use `--skip-download` option", 'info')
            log(f"Repository address: {git_url}")
            exit()
        else:
            log("Repository cloned successfuly.")
    else:
        if not os.path.isdir(repo_dir):
            log("Repository folder not found", "error")
            log(f"If you cloned it change its name to {repo_dir}", 'debug')
            exit()
        else:
            log("Repository folder found successfuly.", "info")
    app_root_path = os.path.join(install_dir, repo_dir)
    if os.path.isdir(app_root_path):
        log("Old installation files already exists, removing them...", "warn")
        try:
            shutil.rmtree(app_root_path)
        except Exception as e:
            log("Error in removing old installation files: " + str(e), "error")
            exit()
    log(f"Installation directory: {install_dir}", "debug")
    try:
        os.makedirs(install_dir, exist_ok=True)
    except Exception as e:
        log("Error in make installtion directory: " + str(e), "error")
        exit()
    try:
        shutil.copytree(repo_dir, app_root_path)
    except Exception as e:
        log("Error in copy cloned directory to installtion directory: " + str(e), "error")
        exit()
    install_dir = os.path.join(install_dir, repo_dir)
    venv_path = os.path.join(install_dir, 'venv')
    os.chdir(install_dir)
    if pythonv in python_versions:
        log("Source code downloaded successfuly, installing[build using pyinstaller]...")
        install_package("pyinstaller")
        install_package("virtualenv")
        subprocess.run([sys.executable, "-m", "venv", venv_path])
        activate_venv(venv_path)
        python_bin_path = os.path.join(venv_path, 'bin', 'python')
        install_package(None, python_bin_path, 'requirements.txt')
        install_package('pyinstaller', python_bin_path)
        subprocess.run(["pyinstaller", "--onefile", "main.py"])
        app_bin_path = os.path.join(install_dir, 'dist', 'main')

        log("Tried to install[build and compile using pyinstaller]")
        log("Result is unknown")
        is_added = add_alias_to_bashrc("aic", f"{app_bin_path} --work-directory {install_dir}")
        os.system("exec $SHELL")
        if is_added:
            log("the AiClient alias added to .bashrc successfuly.")
            log("Now you can run using `aic` command.")
        else:
            log("Maybe the App alias already added to .bashrc")
            log("And you can run using `aic` command.")
        exit()
    else:
        log("Python version not supported, use --info option for see supported python versions", "warn")
        log("you can install the app menualy by following 5 steps: ")
        log(f"step 0 -> First make sure you are in the installtion directory: {install_dir}")
        log("step 1 -> Install the `pyinstaller`, `virtualenv` using `pip install pyinstaller virtualenv`")
        log(f"step 2 -> Create a virtualenv using `{sys.executable} -m venv venv` command")
        log("step 3 -> activate the virtualenv by `source venv/bin/activate` command in Linux and `venv/Scripts/activate` in Windows")
        log("step 4 -> install other python packages using `pip install -r requirements.in` command")
        log("step 5 -> Build the app using `pyinstaller --onefile main.py` command")
        log("Now you can access a executable file in the `dist` directory, its name is `main` in Linux and `main.exe` in Windows")
        log("You can write alias in your .bashrc in Linux or something like that in Windows")
        exit()


if os_name == 'linux':
    log("We don`t support installation on Linux", 'info')
    log("But you can use the source code to install the app on Linux", 'info')
    log("Use `--use-source-code` option for download and install the source code", 'info')
    log("Also you can install the app manually by following 5 steps: ")

    log("You can install the app menualy by following 5 steps: ")
    log(f"step 0 -> First clone the repository from: {git_url} and change your working directory into it", "info")
    log(f"step 1 -> Install the `pyinstaller`, `virtualenv` using `{sys.executable} -m pip install pyinstaller virtualenv`")
    log(f"step 2 -> Create a virtualenv using `{sys.executable} -m venv venv` command")
    log("step 3 -> activate the virtualenv by `source venv/bin/activate` command")
    log(f"step 4 -> install other python packages using `{sys.executable} -m pip install -r requirements.in` command")
    log("step 5 -> Build the app using `pyinstaller --onefile main.py` command")
    log("Now you can access a executable file in the `dist` directory, its name is `main`")
    log("You can write alias in your .bashrc")
    log("Hope you understand")
    log("Thanks for installing")
    exit()
