from webbrowser import open as webbrowser_open
from PyQt5.QtWidgets import QApplication, QMessageBox, QLineEdit, QComboBox, QMainWindow, QCheckBox, QAction, QMenu, QScrollArea, QStatusBar, QMenuBar, QSpacerItem, QWidget, QLabel, QVBoxLayout, QDialog, QPushButton, QTabWidget, QTextEdit, QSizePolicy
from PyQt5.QtCore import QRect, QCoreApplication, QMetaObject, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from functools import partial
from threading import Timer
import core, sys


class AiClientThread(QThread):
    task_completed = pyqtSignal(str, str)  # Signal to emit when the task is completed

    def __init__(self, client, prompt):
        super().__init__()
        self.client = client
        self.prompt = prompt

    def run(self):
        response = self.client.ask(self.prompt)
        status = response[0]  # This is a boolean
        message = response[1] # Provide a default message if status is True
        self.task_completed.emit(str(status), message)  # Emit the result as a string


class ModelSelectionDialog(QDialog):
    def __init__(self, parent=None, service_type="g4f"):
        super(ModelSelectionDialog, self).__init__(parent)
        self.setWindowTitle("Select Model")
        self.setGeometry(100, 100, 300, 400)
        self.layout = QVBoxLayout(self)

        self.models = core.get_available_models(service_type)
        self.model_buttons = []

        for model in self.models:
            button = QPushButton(model)
            button.clicked.connect(lambda checked, m=model: self.select_model(m))
            self.layout.addWidget(button)
            self.model_buttons.append(button)

    def select_model(self, model):
        self.selected_model = model
        self.accept()

def fetch_core_objects():
    main_db_path = core.get_main_database_path()
    db = core.DB(database_path=main_db_path, dictionary=True)
    client = core.AiClient()
    client.database_path = main_db_path
    client.database = db

    return {'database': db,
            'client': client}


class GUI:
    conversion_messages = []
    messages_labels = []
    service_type = "g4f"
    core_objects = fetch_core_objects()
    current_conversion_id = None
    chats = []
    chats_buttons = []
    conversion_messages = []
    service_types = ['Local', 'G4f']
    messages_pov = (5, 5, 445, 20)
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

    def __init__(self):
        self.core_objects['client'].init(service_type=self.service_type.lower())

    def open_settings(self):
        try:
            self.settings_app = SettingsApp()
            self.settings_app.show()
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error in settings", str(e))

    def save_api_key(self):
        api_key = self.api_key_input.toPlainText()
        settings = core.read_settings()
        settings['ai']['api_key'] = api_key
        core.store_settings(settings)

    def setupUi(self, main_window):
        media = core.list_media()
        self.main_window = main_window
        self.main_window.setObjectName("main_window")
        self.main_window.resize(640, 650)
        self.main_window.setWindowIcon(QIcon(media['main_ui']['icon']))
        font = QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.main_window.setFont(font)
        self.main_window.setAutoFillBackground(True)
        self.main_window.setTabShape(QTabWidget.Triangular)
        self._translate = QCoreApplication.translate

        self.main_layout = QWidget(self.main_window)
        self.main_layout.setObjectName("main_layout")
        self.send_button = QPushButton(self.main_layout)
        self.send_button.setGeometry(QRect(560, 400, 71, 31))
        self.send_button.setObjectName("send_button")
        self.prompt_text_edit = QTextEdit(self.main_layout)
        self.prompt_text_edit.setGeometry(QRect(170, 360, 381, 71))
        self.prompt_text_edit.setObjectName("prompt_text_edit")
        self.new_chat_button = QPushButton(self.main_layout)
        self.new_chat_button.setGeometry(QRect(10, 10, 150, 30))
        self.new_chat_button.setObjectName("new_chat_button")
        self.chats_layout_widget = QWidget(self.main_layout)
        self.chats_layout_widget.setGeometry(QRect(10, 50, 151, 381))
        self.chats_layout_widget.setObjectName("chats_layout_widget")
        self.chats_layout = QVBoxLayout(self.chats_layout_widget)
        self.chats_layout.setContentsMargins(0, 0, 0, 0)
        self.chats_layout.setObjectName("verticalLayout")
        self.chats_label = QLabel(self.chats_layout_widget)
        font = QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.chats_label.setFont(font)
        self.chats_label.setObjectName("chats_label")
        self.chats_layout.addWidget(self.chats_label)
        self.update_chats()
        chats_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.chats_layout.addItem(chats_spacer)

        self.messages_layout = QWidget(self.main_layout)
        self.messages_layout.setGeometry(QRect(170, 10, 461, 341))
        self.messages_layout.setObjectName("messages_layout")
        self.chat_layout = QVBoxLayout(self.messages_layout)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setObjectName("chat_layout")

        self.scroll_area = QScrollArea(self.main_layout)  # Use self.main_layout
        self.scroll_area.setWidgetResizable(True)  # Allow the widget to resize
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)

        self.messages_widget = QWidget()  # This will hold the layout for messages
        self.messages_layout = QVBoxLayout(self.messages_widget)  # Create a layout for the messages
        self.messages_widget.setLayout(self.messages_layout)
        self.scroll_area.setWidget(self.messages_widget)
        self.chat_layout.addWidget(self.scroll_area)  # Assuming self.chat_layout is part of self.main_layout

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)

        self.ping_button = QPushButton(self.main_layout)
        self.ping_button.setGeometry(QRect(560, 360, 71, 31))
        self.ping_button.setObjectName("ping_button")
        self.agent_status_label = QLabel(self.main_layout)
        self.agent_status_label.setGeometry(QRect(10, 440, 600, 20))
        font = QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.agent_status_label.setFont(font)
        self.agent_status_label.setObjectName("agent_status_label")
        self.notif_label = QLabel(self.main_layout)
        self.notif_label.setGeometry(QRect(10, 540, 620, 60))
        self.notif_label.setObjectName("notif_label")
        self.notif_label.setDisabled(True)
        self.main_window.setCentralWidget(self.main_layout)
        self.statusbar = QStatusBar(self.main_window)
        self.statusbar.setObjectName("statusbar")
        self.main_window.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(self.main_window)
        self.menubar.setGeometry(QRect(0, 0, 640, 23))
        self.menubar.setObjectName("menubar")
        self.settings_menu = QMenu(self.menubar)
        self.settings_menu.setObjectName("settings_menu")
        self.help_menu = QMenu(self.menubar)
        self.help_menu.setObjectName("help_menu")
        self.about_menu = QMenu(self.menubar)
        self.about_menu.setObjectName("docs_menu")
        self.models_menu = QMenu(self.menubar)
        self.models_menu.setObjectName("models_menu")
        self.other_services = QMenu(self.menubar)
        self.other_services.setObjectName("other_services")
        self.theme_menu = QMenu(self.menubar)
        self.theme_menu.setObjectName("theme_menu")
        self.main_window.setMenuBar(self.menubar)
        self.menubar.addAction(self.settings_menu.menuAction())
        self.menubar.addAction(self.help_menu.menuAction())
        self.menubar.addAction(self.about_menu.menuAction())
        self.menubar.addAction(self.models_menu.menuAction())
        self.menubar.addAction(self.theme_menu.menuAction())

        self.settings_action = QAction("Settings", self.main_window)
        self.docs_action = QAction("Full Documentation", self.main_window)
        self.models_action = QAction("Explor Models", self.main_window)
        self.questions_action = QAction("Questions", self.main_window)
        self.support_action = QAction("Online Support", self.main_window)
        self.about_me_action = QAction("About me", self.main_window)
        self.website_action = QAction("Website", self.main_window)
        self.translator_action = QAction("Translator", self.main_window)
        self.image_generator = QAction("Image Generator", self.main_window)
        self.light_theme_action = QAction("Light theme", self.main_window)
        self.dark_theme_action = QAction("Dark theme", self.main_window)
        self.theme_action = QAction("Change Theme", self.main_window)

        self.about_me_action.triggered.connect(self.about_me)
        self.settings_action.triggered.connect(self.open_settings)
        self.docs_action.triggered.connect(lambda: self.menu_clicked("docs"))
        self.models_action.triggered.connect(lambda: self.menu_clicked("models"))
        self.questions_action.triggered.connect(lambda: self.menu_clicked("questions"))
        self.support_action.triggered.connect(lambda: self.menu_clicked("support"))
        self.website_action.triggered.connect(self.app_website)
        self.translator_action.triggered.connect(self.run_translator)
        self.image_generator.triggered.connect(self.run_image_generator)
        self.light_theme_action.triggered.connect(lambda: self.set_theme('light'))
        self.dark_theme_action.triggered.connect(lambda: self.set_theme('dark'))

        self.models_menu.addAction(self.models_action)
        self.settings_menu.addAction(self.settings_action)
        self.help_menu.addActions([self.docs_action, self.questions_action, self.support_action])
        self.about_menu.addActions([self.about_me_action, self.website_action])
        self.other_services.addActions([self.image_generator, self.translator_action])
        self.theme_menu.addActions([self.dark_theme_action, self.light_theme_action])

        self.menubar.addAction(self.models_menu.menuAction())
        self.menubar.addAction(self.other_services.menuAction())
        self.menubar.addAction(self.settings_menu.menuAction())
        self.menubar.addAction(self.about_menu.menuAction())
        self.menubar.addAction(self.help_menu.menuAction())
        self.menubar.addAction(self.theme_menu.menuAction())

        self.main_window.setWindowTitle(self._translate("main_window", "Ai Client"))
        self.send_button.setText(self._translate("main_window", "Send"))
        self.new_chat_button.setText(self._translate("main_window", "New chat"))
        self.chats_label.setText(self._translate("main_window", "Chats: "))
        self.ping_button.setText(self._translate("main_window", "Ping"))
        self.agent_status_label.setText(self._translate("main_window", "<font color='blue'>Agent is waiting for task...</font>"))
        self.settings_menu.setTitle(self._translate("main_window", "Settings"))
        self.help_menu.setTitle(self._translate("main_window", "Help"))
        self.models_menu.setTitle(self._translate("main_window", "Models"))
        self.theme_menu.setTitle(self._translate("main_window", "Change Theme"))
        self.other_services.setTitle(self._translate("main_window", "Other Services"))
        self.about_menu.setTitle(self._translate("main_window", "About me"))

        self.service_type_combobox= QComboBox(self.main_layout)
        self.service_type_combobox.setGeometry(QRect(10, 465, 200, 30))
        self.service_type_combobox.setObjectName("service_type_combobox")
        for service_type in self.service_types:
            icon = QIcon(media['service_type'][service_type.lower()])
            self.service_type_combobox.addItem(icon, service_type)
        self.service_type_combobox.setCurrentText(self.service_type.lower().capitalize())
        self.core_objects['client'].service_type = self.service_type.lower()
        self.service_type_combobox.currentIndexChanged.connect(self.change_service_type)

        self.api_key_input = QLineEdit(self.main_layout)
        self.api_key_input.setGeometry(QRect(10, 500, 200, 30))
        self.api_key_input.setObjectName("api_key_input")
        self.api_key_input.setPlaceholderText("Enter API key if needed")  # Optional placeholder text

        self.send_button.clicked.connect(self.send_prompt)
        self.new_chat_button.clicked.connect(self.create_new_chat)
        self.ping_button.clicked.connect(self.ping)
        self.api_key_input.editingFinished.connect(self.save_api_key)
        self.set_theme('read')

        QMetaObject.connectSlotsByName(self.main_window)

    def about_me(self):
        about_me_website = core.read_configs()['develop']['website']
        webbrowser_open(about_me_website)

    def set_theme(self, theme='read'):
        if theme == 'read':
            theme = core.read_settings()['ai']['theme']
        if theme == 'dark':
            self.main_window.setStyleSheet(self.dark_theme)
        else:
            self.main_window.setStyleSheet(self.light_theme)
            theme = 'light'
        settings = core.read_settings()
        settings['ai']['theme'] = theme
        core.store_settings(settings)
        self.show_notif(f"Application theme set to {theme}")

    def app_website(self):
        app_website = core.read_configs()['develop']['app_website']
        webbrowser_open(app_website)

    def run_translator(self):
        try:
            from plugins.Translator.app import TranslatorApp
            self.translator_window = QMainWindow()
            self.translator_app = TranslatorApp()
            self.translator_app.setupUi(self.translator_window)
            self.translator_window.show()
        except Exception as e:
            self.show_notif("Error in running translator: " + str(e), color='red', during=10)

    def destroy_notif(self):
        self.notif_label.hide()

    def run_image_generator(self):
        try:
            from plugins.ImageGenerator.app import ImageGeneratorApp
            self.image_generator_app = ImageGeneratorApp()
            self.image_generator_app.show()
        except Exception as e:
            self.show_notif("Error in running image generator: " + str(e), color='red', during=10)

    def menu_clicked(self, action):
        print("Action:", action)

    def send_prompt(self):
        if not self.current_conversion_id:
            return self.show_notif("First start a new chat or select an existing chat on the left side.", color='red')

        self.agent_status_label.setText(
            self._translate("main_window", "<font color='green'>Agent is running task...</font>"))
        self.api_key = self.api_key_input.text()
        self.core_objects['client'].api_key = self.api_key
        self.agent_status_label.update()  # Update the label immediately

        prompt = self.prompt_text_edit.toPlainText()
        self.prompt_text_edit.clear()
        self.temp_prompt = prompt
        self.core_objects['client'].conversion_id = self.current_conversion_id

        # Create and start the thread
        self.ai_client_thread = AiClientThread(self.core_objects['client'], prompt)
        self.ai_client_thread.task_completed.connect(self.on_task_completed)
        self.ai_client_thread.start()

    def on_task_completed(self, status, message):
        status = True if status == 'True' else False
        if not status:
            self.show_notif(message, color='red', during=8)
            return

        is_first_message = len(self.conversion_messages) == 0
        if is_first_message:  # update and set conversion title if it's the first message in conversion
            title = self.temp_prompt
            if len(title) > 15:
                title = f"{title[:15]}..."  # set the first 15 characters of prompt for title of the conversion
            self.core_objects['client'].database.update_conversion(self.current_conversion_id, title)
            self.update_chats()

        self.load_conversion_messages(self.current_conversion_id)
        self.agent_status_label.setText(
            self._translate("main_window", "<font color='blue'>Agent is waiting for task...</font>"))

    def show_notif(self, message, during=3, color: str = 'blue', font=None):
        core.log(f"NOTIF: {message}", 'debug')
        settings = core.read_settings()['ai']
        if settings['show_notif'] == "OFF":
            return
        if settings['notif_type'] == "messagebox":
            if color == 'red':
                return QMessageBox.critical(self.main_window, "NOTIF", message)
            elif color == 'yellow':
                return QMessageBox.warning(self.main_window, "NOTIF", message)
            else:
                return QMessageBox.information(self.main_window, "NOTIF", message)
        else:
            if font:
                self.notif_label.setFont(font)
            else:
                font = QFont()
                font.setFamily("Noto Sans")
                font.setPointSize(10)
                font.setBold(True)
                self.notif_label.setFont(font)
            self.notif_label.setStyleSheet(
                "background-color: white; border: 1px solid black; border-radius: 10px; padding: 5px;")
            self.notif_label.setText(self._translate("main_window", f"<font color='{color}'>{message}</font>"))
            self.notif_label.setEnabled(True)
            self.notif_label.show()
            Timer(during, self.destroy_notif).start()

    def ping(self):
        font = QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(True)
        self.show_notif('Engine is online!', 3, font=font)

    def create_new_chat(self):
        dialog = ModelSelectionDialog(service_type=self.service_type)
        if dialog.exec_() == QDialog.Accepted:
            selected_model = dialog.selected_model
            self.core_objects['client'].database.record_conversion(title="A new chat", model_id=core.get_model_info(name=selected_model, database=self.core_objects['database'])['id'])
            self.show_notif("new chat created, please select it if you want to send prompt", 3, color='green')
            self.update_chats()

    def update_chats(self):
        # Destroy existing chat buttons
        for chat_obj in self.chats_buttons:
            chat_obj.deleteLater()
        self.chats_buttons.clear()  # Clear the list after destroying

        # Fetch new chats
        self.chats = self.core_objects['client'].database.get_conversions()

        # Create new chat buttons
        for index, chat_info in enumerate(self.chats):
            chat_title = chat_info['title']
            chat_id = chat_info['id']
            chat = QPushButton(self.chats_layout_widget)
            chat.setObjectName(f"chat{index}")
            self.chats_layout.addWidget(chat)
            chat.setText(self._translate("main_window", str(chat_title)))
            func = partial(self.load_conversion_messages, chat_id)  # Use partial to pass chat_id
            chat.clicked.connect(func)  # Connect button click to load messages
            self.chats_buttons.append(chat)

    def load_conversion_messages(self, conversion_id):
        # Clear existing messages
        while self.messages_layout.count():  # While there are items in the layout
            item = self.messages_layout.takeAt(0)  # Take the first item
            if item.widget():  # If it's a widget, delete it
                item.widget().deleteLater()  # Schedule for deletion

        self.current_conversion_id = int(conversion_id)
        self.conversion_messages = self.core_objects['client'].database.get_conversion_messages(
            self.current_conversion_id)

        # Check if messages were retrieved
        if not self.conversion_messages:
            no_message_label = QLabel("No messages available for this chat.", self.messages_widget)
            self.messages_layout.addWidget(no_message_label)
            return

        for message_info in self.conversion_messages:
            message_id = message_info['id']
            message_text = message_info['message']
            message_author = message_info['role']

            # Create message label
            message_label = QLabel(self.messages_widget)  # Use messages_widget as parent
            message_label.setWordWrap(True)  # Enable word wrapping
            message_label.setText(f"{message_author}: {message_text}")

            # Add to layout
            self.messages_layout.addWidget(message_label)

        # Add stretch at the end to push messages to the top
        self.messages_layout.addStretch()

        # Update the scroll area to ensure it displays the new messages
        self.scroll_area.update()

    def change_service_type(self, new_service_type_index):
        self.service_type = self.service_types[int(new_service_type_index)].lower()
        settings = core.read_settings()
        settings['ai']['service_type'] = self.service_type
        core.store_settings(settings)
        self.show_notif(f"Service type changed to {self.service_type}")


class SettingsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Notification Settings App')
        self.setGeometry(100, 100, 300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.notification_checkbox = QCheckBox('Show Notifications')
        self.notification_checkbox.setChecked(True)  # Default to ON

        self.notification_type_label = QLabel('Notification Type:')
        self.notification_type_combo = QComboBox()
        self.notification_type_combo.addItems(['Label in Bottom', 'Message Box'])
        notif_type = core.read_settings()['ai']['notif_type']
        self.notification_type_combo.setCurrentText('Label in Bottom' if notif_type == 'label' else 'Message Box')

        self.save_button = QPushButton('Save Settings')
        self.save_button.clicked.connect(self.save_settings)

        layout.addWidget(self.notification_checkbox)
        layout.addWidget(self.notification_type_label)
        layout.addWidget(self.notification_type_combo)
        layout.addWidget(self.save_button)

    def save_settings(self):
        show_notifications = self.notification_checkbox.isChecked()
        notification_type = self.notification_type_combo.currentText()

        status = "ON" if show_notifications else "OFF"
        notif_type = "label" if notification_type == 'Label in Bottom' else 'messagebox'
        settings = core.read_settings()
        settings['ai']['notif_type'] = notif_type
        settings['ai']['show_notif'] = status
        core.store_settings(settings)
        QMessageBox.information(self, "success", "Settings saved!")



def run_gui():
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = GUI()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
