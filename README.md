# AiClient 🚀

A free unlimited multi interface (GUI, CLI) AI client for Linux and Windows which was developed with Python, PyQt5, g4f

# Note 📌
This project is still under development and no one knows about it, that's why it doesn't have many stars or views 🤗😀

# Donate and keep this project open source 🙏
Trc20 `TGTquY2FjJyCujwrYt6aYdwxQVaX8vkoxX`

ETH `0x06aECEe6aFa7D7ec4A195cd6e15a4354143B647c`

BTC `bc1qa0s0l69vx0006yn69x00t5wqey3p3q7ra0xuh6`

BNB `0x06aECEe6aFa7D7ec4A195cd6e15a4354143B647c`

# Install ⚙️

#### Windows 🪟
Installation on Windows is so easy!
Just download the app last release in Release Section with `.msi` or `.exe` format and launch it then follow the steps to install the app

#### Linux 🐧

we just support Windows auto GUI installer and if you are using Linux, its recommended to install from the source code

## Install from the source code 🧰

First clone the project from this GitHub repository and change current directory into cloned directory

```bash
git clone https://github.com/LinuxV3/AiClient
cd AiClient
```
then you have to install the project requirements using `pip`

```bash
pip install -r requirements.txt
```
Now you can start using AI models by launching the App
```bash
python3 main.py
```
## Build using `pyinstaller` 🛠️
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
pip install -r requirements.txt
```
Now you can build the app using `pyinstaller`
```bash
pyinstaller --onefile main.py
```
After build the app you can run the executable file which was created in `dist/main`
Hope to enjoy your using !

## Usage 🔰

The app is so User-Friendly and has a GUI interface so it does not need to any guide or docs but We created a PDF document for anyone who do not know how to use the App

The full docs `.PDF` file designed and is ready in `UserGuide.pdf` file in the GitHub repository
also you can download it [from here](https://aiclient.pythonanywhere.com/src/UserGuide.pdf)



## License 🪪

[GNU Affero General Public License v3.0](https://choosealicense.com/licenses/agpl-3.0/)