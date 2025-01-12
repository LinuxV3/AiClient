import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTextEdit, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QSlider, QFileDialog, QHBoxLayout, QAction
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PIL import Image
from g4f import Client as g4f_client
from os.path import expanduser
import io
from re import findall
import core


class ImageGeneratorThread(QThread):
    result_ready = pyqtSignal(list)
    def __init__(self, prompt, service_type, model):
        super().__init__()
        self.prompt = prompt
        self.service_type = service_type
        self.model = model
    def run(self):
        result = generate_image(self.prompt, self.service_type, self.model)
        self.result_ready.emit(result)


class OneArgThread(QThread):
    def __init__(self, arg, func, app_self):
        super().__init__()
        self.arg = arg
        self.func = func
        self.app_self = app_self
        self.app_self.is_thread_did = False
    def run(self):
        result = self.func(self.arg)
        self.app_self.thread_result = result
        self.app_self.is_thread_did = True


class TwoArgThread(QThread):
    def __init__(self, arg1, arg2, func, app_self):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self.func = func
        self.app_self = app_self
        self.app_self.is_thread_did = False
    def run(self):
        result = self.func(self.arg1, self.arg2)
        self.app_self.thread_result = result
        self.app_self.is_thread_did = True


class SettingsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        settings = core.read_settings()['image_generator']
        self.setWindowTitle('Settings App')
        self.setGeometry(100, 100, 300, 200)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # NSFW Level ComboBox
        self.nsfw_label = QLabel('NSFW Level:')
        self.nsfw_combo = QComboBox()
        self.nsfw_combo.addItems(['Low', 'Medium', 'High'])
        core.log(f"NSFW will set to {settings['nsfw_level']}", 'info')

        # Image Width TextEdit
        self.width_label = QLabel('Image Show Width:')
        self.width_edit = QTextEdit()
        self.width_edit.setFixedHeight(30)
        self.width_edit.insertPlainText(str(settings['images_show_width']))

        # Image Height TextEdit
        self.height_label = QLabel('Image Show Height:')
        self.height_edit = QTextEdit()
        self.height_edit.setFixedHeight(30)
        self.height_edit.insertPlainText(str(settings['images_show_height']))

        # Save Button
        self.save_button = QPushButton('Save Settings')
        self.save_button.clicked.connect(self.save_settings)

        # Add widgets to layout
        layout.addWidget(self.nsfw_label)
        layout.addWidget(self.nsfw_combo)
        layout.addWidget(self.width_label)
        layout.addWidget(self.width_edit)
        layout.addWidget(self.height_label)
        layout.addWidget(self.height_edit)
        layout.addWidget(self.save_button)
        self.nsfw_combo.setCurrentText(settings['nsfw_level'].capitalize())

    def save_settings(self):
        try:
            nsfw_level = self.nsfw_combo.currentText().lower()
            width_text = self.width_edit.toPlainText()
            height_text = self.height_edit.toPlainText()
            width = int(width_text)
            height = int(height_text)

            if width <= 0 or height <= 0:
                raise ValueError("Width and Height must be greater than 0.")
            settings = core.read_settings()
            settings['image_generator']['nsfw_level'] = nsfw_level.lower()
            settings['image_generator']['images_show_width'] = width
            settings['image_generator']['images_show_height'] = height
            core.store_settings(settings)
            QMessageBox.information(self, "success", 'Settings Saved')
        except ValueError as e:
            QMessageBox.warning(self, 'Input Error',
                                str(e) + "\nPlease enter valid values.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f'Error Occurred\n{e}')


def get_error_message_image():
    image = core.list_media()['image_generator']['error']
    with open(image, "rb") as file:
        content = file.read()
    return Image.open(io.BytesIO(content))


def get_welcome_image():
    image = core.list_media()['image_generator']['welcome']
    with open(image, "rb") as file:
        content = file.read()
    return Image.open(io.BytesIO(content))


def check_nsfw(text, level):
    try:
        is_sexual = requests.get("https://aiclient.pythonanywhere.com/api/check_nsfw", params={'text': text, 'level': level}).json()['is_sexual']
    except:
        return False
    return is_sexual


def generate_image(prompt, service_type, model):
    response = generate_image_(prompt=prompt, model=model, service_type=service_type)
    core.log(f"Response in generate image: {response}", 'info')
    status = response[0]
    if status:
        images = []
        images_url = response[1]
        if images_url and isinstance(images_url, list) and len(images_url) >= 1:
            images_url = list(set(images_url))  
            for image_url in images_url:
                isok = False
                try:
                    response = requests.get(image_url)
                    status_code = response.status_code
                    if status_code == 200:
                        images.append(Image.open(io.BytesIO(response.content)))
                        isok = True
                    else:
                        isok = False
                        core.log(f"status code is {response.status_code}", 'debug')
                except Exception as e:
                    isok = False
                if not isok:
                    try:
                        images.append(get_error_message_image())
                    except:
                        pass
            if images:
                return [True, images]
            else:
                return [False, f"Failed to fetch images, Try again!"]
        else:
            return [False, images_url]
    else:
        if "NSFW content detected" in response[1]:
            return [False, "NSFW content detected, more info at https://en.wikipedia.org/wiki/Not_safe_for_work"]
        return [False, response[1]]


def find_image_urls(response):
    result = findall(r'https?://[^\s\)]+', response)
    return result


def check_network(timeout_time=None):
    ping_url = "http://google.com/"
    dns_problem_url = "http://8.8.8.8"
    default_timeout = 5

    if not timeout_time:
        timeout_time = default_timeout
    try:
        if requests.get(ping_url, timeout=timeout_time).status_code == 200:
            return [True, "Success"]
        else:
            raise ValueError("Status code issues.")
    except Exception as e:
        error_text = str(e)
        if 'Read timed out' in error_text:
            return [False, "the Internet is so poor"]
        elif "Name or service not known" in error_text:
            try:
                if requests.get(dns_problem_url, timeout=timeout_time).status_code == 200:
                    return [False, "you have DNS problem"]
                else:
                    return [False, "Internet connection error"]
            except:
                pass
        return [False, f"No Internet connection! -> {error_text}"]


def generate_image_(service_type, prompt, model):
    client = core.AiClient()
    client.init(ignore_database=True, model=model, service_type=service_type)
    try:
        response = client.ask(prompt=prompt)
    except Exception as e:
        return [False, str(e)]
    else:
        if response[0]:
            return [True, find_image_urls(response[1])]
        else:
            return response


class ImageGeneratorApp(QMainWindow):
    service_types = ['local', 'g4f']
    is_first_try = True
    is_display_size_info = True
    light_theme = """
        QMainWindow, QWidget {
            background-color: #ffffff;
            color: #000000;
        }
        QTextEdit {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #6272a4;
            color: #ffffff;
            border-radius: 6px;
            height: 40px;
            border: none;
        }
        QPushButton:hover {
            background-color: #4a5a82;
        }
        QLabel {
            color: #444444;
        }
        QComboBox {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #cccccc;
            border-radius: 4px;
        }
    """
    dark_theme = """
        QMainWindow, QWidget {
            background-color: #282a36;
            color: #f8f8f2;
        }
        QTextEdit {
            background-color: #44475a;
            color: #f8f8f2;
            border: 1px solid #6272a4;
            border-radius: 4px;
        }
        QPushButton {
            background-color: #bd93f9;
            color: #ffffff;
            border-radius: 6px;
            height: 40px;
            border: none;
        }
        QPushButton:hover {
            background-color: #9d79d1;
        }
        QLabel {
            color: #f8f8f2;
        }
        QComboBox {
            background-color: #44475a;
            color: #f8f8f2;
            border: 1px solid #6272a4;
            border-radius: 4px;
        }
    """

    def open_settings(self):
        self.settings_app = SettingsApp()
        self.settings_app.show()

    def __init__(self):
        self.settings = core.read_settings()['image_generator']
        self.current_theme = self.settings['theme']
        self.service_type = self.settings['service_type']
        self.model = self.settings['model']
        if isinstance(self.model, dict): # if self.model is a dict of {'id': 'model_name', 'owned_by': 'model_owner'}
            self.model = self.model['id']
        self.models = core.read_configs()['models']['available'][self.service_type]['image']
        super().__init__()
        self.initUI()

    def check_network(self, _=None, show_success=True):
        is_success, msg = check_network()
        func = None
        if is_success and show_success:
            msg = "You are connected to an establish network."
            func = QMessageBox.information
        elif not is_success:
            func = QMessageBox.critical
        if func:
            func(self, "Connection status", msg)
        return is_success
    
    def check_net(self, show_success):
        if self.is_first_try:
            result = self.check_network(show_success=show_success)
            self.is_first_try = not result
            return result
        else:
            return True

    def initUI(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Settings')

        settings_action = QAction('Open Settings', self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)

        theme_menu = menubar.addMenu('Theme')
        light_theme_action = QAction('Light Theme', self)
        dark_theme_action = QAction('Dark Theme', self)
        light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))
        theme_menu.addAction(dark_theme_action)
        theme_menu.addAction(light_theme_action)

        network_menu = menubar.addMenu('Make sure you are connected to internet!')
        network_action = QAction('Check Network', self)
        network_action.triggered.connect(self.check_network)
        network_menu.addAction(network_action)

        self.default_directory = expanduser('~')
        self.setWindowTitle('Image Generator')
        self.setGeometry(100, 100, 530, 740)

        layout = QVBoxLayout()

        self.prompt_input = QLineEdit(self)
        self.prompt_input.setPlaceholderText('Enter prompt')
        layout.addWidget(self.prompt_input)

        service_type_layout = QHBoxLayout()
        self.service_type_label = QLabel('Service Type:', self)
        service_type_layout.addWidget(self.service_type_label)

        self.service_type_input = QComboBox(self)
        self.service_type_input.addItems(self.service_types)
        self.service_type_input.currentIndexChanged.connect(self.change_service_type)
        self.service_type_input.setCurrentText(self.service_type)
        service_type_layout.addWidget(self.service_type_input)
        layout.addLayout(service_type_layout)
        
        model_layout = QHBoxLayout()
        self.model_label = QLabel('Model:', self)
        model_layout.addWidget(self.model_label)

        self.model_input = QComboBox(self)
        self.model_input.addItems([model['id'] for model in self.models])
        self.model_input.currentIndexChanged.connect(self.change_model)
        self.model_input.setCurrentText(self.model)
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)

        self.generate_button = QPushButton('Generate Image', self)
        self.generate_button.clicked.connect(self.generate_image)
        layout.addWidget(self.generate_button)

        self.save_image_button = QPushButton('Save Image', self)
        self.save_image_button.clicked.connect(self.save_image)
        layout.addWidget(self.save_image_button)

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)
    
        self.slider = QSlider(self)
        self.slider.setOrientation(1)  
        self.slider.valueChanged.connect(self.update_image)
        self.slider.setDisabled(True)
        layout.addWidget(self.slider)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        """print('''
    QPushButton {
        background-color: #4CAF50;  /* Green */
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
    }
    QLineEdit {
        background-color: #f1f1f1;  /* Light grey */
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    QComboBox {
        background-color: #f1f1f1;  /* Light grey */
        border: 1px solid #ccc;
        border-radius: 5px;
    }
    QComboBox::drop-down {
        background-color: #f1f1f1;  /* Light grey */
    }
    QComboBox::item {
        background-color: #f1f1f1;  /* Light grey */
        color: #000000;  /* Black text */
    }
    QComboBox::item:hover {
        background-color: #4CAF50;  /* Green */
        color: #FFFF00;  /* White */
    }
''')"""
        self.show_welcome_image()
        self.update_theme()

    def set_theme(self, theme):
        if theme == 'dark':
            self.current_theme = 'dark'
        elif theme == 'light':
            self.current_theme = 'light'
        elif theme == 'toggle':
            self.current_theme = 'dark' if self.current_theme == 'light' else 'light'
        else:
            self.current_theme = 'dark'
        self.update_theme()

    def update_theme(self):
        if self.current_theme == 'dark':
            self.setStyleSheet(self.dark_theme)
        elif self.current_theme == 'light':
            self.setStyleSheet(self.light_theme)
        else:
            self.current_theme = "dark"
            return self.update_theme()
        settings = core.read_settings()
        settings['image_generator']['theme'] = self.current_theme
        core.store_settings(settings)
    
    def show_welcome_image(self):
        try:
            image = get_welcome_image()
            image = image.convert("RGBA")  
            data = image.tobytes("raw", "RGBA")
            qimage = QImage(data, image.width , image.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            
            desired_width = self.settings['images_show_width']
            desired_height = self.settings['images_show_height']
            pixmap = pixmap.scaled(desired_width, desired_height, aspectRatioMode=Qt.KeepAspectRatio)  
            self.image_label.setPixmap(pixmap)  
        except Exception as e:
            raise e

    def change_service_type(self, service_type_index):
        self.service_type = self.service_types[service_type_index]
        self.models = core.read_configs()['models']['available'][self.service_type]['image']
        settings = core.read_settings()
        settings['image_generator']['service_type'] = self.service_type
        core.store_settings(settings)

    def change_model(self, model_index):
        self.model = self.models[model_index]['id']
        settings = core.read_settings()
        settings['image_generator']['model'] = self.model
        core.store_settings(settings)

    def generate_image(self):
        if not self.check_net(False):
            return
        prompt = self.prompt_input.text()
        if not prompt:
            QMessageBox.critical(self, "Error", "Please enter a prompt.")
            return
        nsfw_level = self.settings['nsfw_level']
        if check_nsfw(text=prompt, level=nsfw_level):
            QMessageBox.critical(self, "hmm...", "NSFW content detected, more info at https://en.wikipedia.org/wiki/Not_safe_for_work")
            return
        service_type = self.service_type
        model = self.model
        self.thread = ImageGeneratorThread(prompt, service_type, model)
        self.thread.result_ready.connect(self.process_generated_images_result)
        self.thread.start()

    def process_generated_images_result(self, func_result):
        success, result = func_result[0], func_result[1]

        if success:
            self.images = result
            if len(self.images) == 1:
                self.slider.setDisabled(True)
            else:
                self.slider.setEnabled(True)
                self.slider.setMaximum(len(self.images) - 1)
            self.update_image(0)
        else:
            QMessageBox.critical(self, 'Error', result)

    def update_image(self, value):
        if hasattr(self, 'images') and self.images:
            image = self.images[value]
            if isinstance(image, Image.Image):
                original_width, original_height = image.size
                image = image.convert("RGBA")
                data = image.tobytes("raw", "RGBA")
                qimage = QImage(data, image.width , image.height, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage)
                desired_width = self.settings['images_show_width']
                desired_height = self.settings['images_show_height']
                pixmap = pixmap.scaled(desired_width, desired_height, aspectRatioMode=Qt.KeepAspectRatio)
                self.image_label.setPixmap(pixmap)  
                now_width = pixmap.width()
                now_height = pixmap.height()
                if self.is_display_size_info:
                    self.is_display_size_info = True
                    message = f"Images original size is {original_width}x{original_height} but for display whole of the image, image is displaying in {now_width}x{now_height} size"
                    QMessageBox.information(self, "Image Size Information", message)

    def save_image(self):
        if hasattr(self, 'images') and self.images:
            current_image = self.images[self.slider.value()]
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", self.default_directory,
                                                       "PNG Files (*.png)",
                                                       options=options)
            
            if file_name:
                if not file_name.lower().endswith('.png'):
                    file_name += '.png'
                try:
                    current_image.save(file_name)
                    QMessageBox.information(self, "Image Saved", "Image has been saved successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save image: {e}")
        else:
            QMessageBox.warning(self, "No Image", "There is no image to save.")


def run(sys_exit: bool=True):
    app = QApplication(sys.argv)
    ex = ImageGeneratorApp()
    ex.show()
    app.exec_()
    if sys_exit:
        sys.exit(app.exec_())


"""if __name__ == "__main__":
    run()"""
