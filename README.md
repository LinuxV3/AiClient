# AiClient

A free unlimited multi interface (GUI, CLI) AI client for Linux and Windows which was developed with Python, PyQt5, g4f


# Install using install script
#### Windows
Installation on Windows is so easy!
Just download the app last release in Release Section with `.msi` or `.exe` format and launch it then follow the steps to install the app
#### Linux
Unfortunately we just support Debian-based Linux distribution and for other distribution you can install and build the app from the source code

So for Debian-based distribution like Ubuntu, Debian, Mint Linux or other download the app last release in Release Section with `.deb` format

then run the following command to install it by `apt` package manager.

```bash
sudo apt install "downloaded_file_path"
```

## Install from the source code

First clone the project from this GitHub repository and change current directory into cloned directory

```bash
git clone https://github.com/LinuxV3/AiClient
cd AiClient
```
then you have to install the project requirements using `pip`

```bash
pip install -r requirements.in
```
Now you can start using AI models by launching the App
```bash
python3 main.py
```
### Build using `pyinstaller`
Also after you can build the project and make an executable file using `pyinstaller`

First make sure you cloned the repository and you are in the cloned directory

Then install the `pyinstaller` and `virtualenv` packages using `pip`
```bash
pip install pyinstaller virtualenv
```

After that create a virtualenv by running the following command
```bash
python3 -m venv venv
```

Then activate the virtualenv using bellow command
```bash
source venv/bin/activate
```

Install the requirements using `pip`
```bash
pip install -r requirements.in
```
Now you can build the app using `pyinstaller`
```bash
pyinstaller --onefile main.py
```
After build the app you can run the executable file which was created in `dist/main`
Hope to enjoy your using !

## Usage

The app is so User-Friendly and has a GUI interface so it doesn`t need to any guide or docs but We created a pdf document for anyone who don`t know how to use the App

The full docs `.pdf` file designed and is ready in `UserGuide.pdf` file in the GitHub repository
also you can download it [from here](https://aiclient.pythonanywhere.com/src/UserGuide.pdf)



## License

[GNU Affero General Public License v3.0](https://choosealicense.com/licenses/agpl-3.0/)
