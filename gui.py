from webbrowser import open as webbrowser_open  # Importing webbrowser to open URLs
from PyQt5.QtWidgets import QApplication, QMessageBox, QLineEdit, QComboBox, QMainWindow, QCheckBox, QAction, QMenu, QScrollArea, QStatusBar, QMenuBar, QSpacerItem, QWidget, QLabel, QVBoxLayout, QDialog, QPushButton, QTabWidget, QTextEdit, QSizePolicy  # Importing necessary PyQt5 widgets
from PyQt5.QtCore import QRect, QCoreApplication, QMetaObject, QThread, pyqtSignal  # Importing core functionalities from PyQt5
from PyQt5.QtGui import QFont, QIcon  # Importing font and icon classes from PyQt5
from functools import partial  # Importing partial for creating partial functions
from threading import Timer  # Importing Timer for delayed execution
import core, sys  # Importing core functionalities and system module


class AiClientThread(QThread):
    """Thread class to handle asynchronous tasks related to the AI client."""
    task_completed = pyqtSignal(str, str)  # Signal to emit when the task is completed

    def __init__(self, client, prompt):
        """Initialize the thread with the client and prompt."""
        super().__init__()
        self.client = client  # AI client instance
        self.prompt = prompt  # Prompt to be sent to the AI client

    def run(self):
        """Run the thread to process the prompt and emit the result."""
        response = self.client.ask(self.prompt)  # Get response from the AI client
        status = response[0]  # This is a boolean indicating success
        message = response[1]  # Provide a default message if status is True
        self.task_completed.emit(str(status), message)  # Emit the result as a string


class ModelSelectionDialog(QDialog):
    """Dialog for selecting models."""
    def __init__(self, parent=None, service_type="g4f"):
        """Initialize the model selection dialog."""
        super(ModelSelectionDialog, self).__init__(parent)
        self.setWindowTitle("Select Model")  # Set dialog title
        self.setGeometry(100, 100, 300, 400)  # Set dialog size
        self.layout = QVBoxLayout(self)  # Set layout for the dialog

        self.models = core.get_available_models(service_type)  # Get available models
        self.model_buttons = []  # List to hold model buttons

        for model in self.models:
            button = QPushButton(model)  # Create a button for each model
            button.clicked.connect(lambda checked, m=model: self.select_model(m))  # Connect button click to model selection
            self.layout.addWidget(button)  # Add button to layout
            self.model_buttons.append(button)  # Append button to the list

    def select_model(self, model):
        """Select a model and accept the dialog."""
        self.selected_model = model  # Store the selected model
        self.accept()  # Close the dialog


def fetch_core_objects():
    """Fetch core objects needed for the application."""
    main_db_path = core.get_main_database_path()  # Get the main database path
    db = core.DB(database_path=main_db_path, dictionary=True)  # Initialize the database
    client = core.AiClient()  # Create an AI client instance
    client.database_path = main_db_path  # Set the database path for the client
    client.database = db  # Assign the database to the client

    return {'database': db, 'client': client}  # Return core objects as a dictionary


class GUI:
    """Main class for the graphical user interface."""
    conversion_messages = []  # List to hold conversion messages
    messages_labels = []  # List to hold message labels
    service_type = "g4f"  # Default service type
    core_objects = fetch_core_objects()  # Fetch core objects
    current_conversion_id = None  # Current conversion ID
    chats = []  # List to hold chat information
    chats_buttons = []  # List to hold chat buttons
    conversion_messages = []  # List to hold conversion messages
    service_types = ['Local', 'G4f']  # Available service types
    messages_pov = (5, 5, 445, 20)  # Position of messages
    # Dark theme stylesheet
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
    # Light theme stylesheet
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
        """Initialize the GUI and set up the client."""
        self.core_objects['client'].init(service_type=self.service_type.lower())  # Initialize the client with the service type

    def open_settings(self):
        """Open the settings application."""
        try:
            self.settings_app = SettingsApp()  # Create an instance of SettingsApp
            self.settings_app.show()  # Show the settings window
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error in settings", str(e))  # Show error message if settings fail to open

    def save_api_key(self):
        """Save the API key entered by the user."""
        api_key = self.api_key_input.toPlainText()  # Get the API key from input
        settings = core.read_settings()  # Read current settings
        settings['ai']['api_key'] = api_key  # Update the API key in settings
        core.store_settings(settings)  # Store updated settings

    def setupUi(self, main_window):
        """Set up the user interface components."""
        media = core.list_media()  # List media resources
        self.main_window = main_window  # Set the main window
        self.main_window.setObjectName("main_window")  # Set object name for the main window
        self.main_window.resize(640, 650)  # Resize the main window
        self.main_window.setWindowIcon(QIcon(media['main_ui']['icon']))  # Set window icon
        font = QFont()  # Create a font object
        font.setFamily("Noto Sans")  # Set font family
        font.setPointSize(10)  # Set font size
        font.setBold(True)  # Set font to bold
        font.setWeight(75)  # Set font weight
        self.main_window.setFont(font)  # Apply font to the main window
        self.main_window.setAutoFillBackground(True)  # Enable auto-fill background
        self.main_window.setTabShape(QTabWidget.Triangular)  # Set tab shape
        self._translate = QCoreApplication.translate  # Set translation function

        self.main_layout = QWidget(self.main_window)  # Create main layout widget
        self.main_layout.setObjectName("main_layout")  # Set object name for the layout
        self.send_button = QPushButton(self.main_layout)  # Create send button
        self.send_button.setGeometry(QRect(560, 400, 71, 31))  # Set button geometry
        self.send_button.setObjectName("send_button")  # Set object name for the button
        self.prompt_text_edit = QTextEdit(self.main_layout)  # Create text edit for prompt
        self.prompt_text_edit.setGeometry(QRect(170, 360, 381, 71))  # Set geometry for text edit
        self.prompt_text_edit.setObjectName("prompt_text_edit")  # Set object name for text edit
        self.new_chat_button = QPushButton(self.main_layout)  # Create new chat button
        self.new_chat_button.setGeometry(QRect(10, 10, 150, 30))  # Set geometry for new chat button
        self.new_chat_button.setObjectName("new_chat_button")  # Set object name for new chat button
        self.chats_layout_widget = QWidget(self.main_layout)  # Create widget for chat layout
        self.chats_layout_widget.setGeometry(QRect(10, 50, 151, 381))  # Set geometry for chat layout widget
        self.chats_layout_widget.setObjectName("chats_layout_widget")  # Set object name for chat layout widget
        self.chats_layout = QVBoxLayout(self.chats_layout_widget)  # Create vertical layout for chats
        self.chats_layout.setContentsMargins(0, 0, 0, 0)  # Set margins for chat layout
        self.chats_layout.setObjectName("verticalLayout")  # Set object name for vertical layout
        self.chats_label = QLabel(self.chats_layout_widget)  # Create label for chats
        font = QFont()  # Create font object for chats label
        font.setFamily("Noto Sans")  # Set font family
        font.setPointSize(10)  # Set font size
        font.setBold(True)  # Set font to bold
        font.setItalic(True)  # Set font to italic
        font.setUnderline(False)  # Set underline to false
        font.setWeight(75)  # Set font weight
        self.chats_label.setFont(font)  # Apply font to chats label
        self.chats_label.setObjectName("chats_label")  # Set object name for chats label
        self.chats_layout.addWidget(self.chats_label)  # Add chats label to layout
        self.update_chats()  # Update chat list
        chats_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)  # Create spacer for chats layout
        self.chats_layout.addItem(chats_spacer)  # Add spacer to layout

        self.messages_layout = QWidget(self.main_layout)  # Create widget for messages layout
        self.messages_layout.setGeometry(QRect(170, 10, 461, 341))  # Set geometry for messages layout
        self.messages_layout.setObjectName("messages_layout")  # Set object name for messages layout
        self.chat_layout = QVBoxLayout(self.messages_layout)  # Create vertical layout for chat messages
        self.chat_layout.setContentsMargins(0, 0, 0, 0)  # Set margins for chat layout
        self.chat_layout.setObjectName("chat_layout")  # Set object name for chat layout

        self.scroll_area = QScrollArea(self.main_layout)  # Create scroll area for messages
        self.scroll_area.setWidgetResizable(True)  # Allow the widget to resize
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)  # Set frame shape for scroll area

        self.messages_widget = QWidget()  # Create widget to hold messages layout
        self.messages_layout = QVBoxLayout(self.messages_widget)  # Create layout for messages
        self.messages_widget.setLayout(self.messages_layout)  # Set layout for messages widget
        self.scroll_area.setWidget(self.messages_widget)  # Set messages widget in scroll area
        self.chat_layout.addWidget(self.scroll_area)  # Add scroll area to chat layout

        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Set size policy for buttons
        size_policy.setHorizontalStretch(0)  # No horizontal stretch
        size_policy.setVerticalStretch(0)  # No vertical stretch

        self.ping_button = QPushButton(self.main_layout)  # Create ping button
        self.ping_button.setGeometry(QRect(560, 360, 71, 31))  # Set geometry for ping button
        self.ping_button.setObjectName("ping_button")  # Set object name for ping button
        self.agent_status_label = QLabel(self.main_layout)  # Create label for agent status
        self.agent_status_label.setGeometry(QRect(10, 440, 600, 20))  # Set geometry for agent status label
        font = QFont()  # Create font object for agent status label
        font.setFamily("Noto Sans")  # Set font family
        font.setPointSize(10)  # Set font size
        font.setBold(True)  # Set font to bold
        font.setItalic(True)  # Set font to italic
        font.setWeight(75)  # Set font weight
        self.agent_status_label.setFont(font)  # Apply font to agent status label
        self.agent_status_label.setObjectName("agent_status_label")  # Set object name for agent status label
        self.notif_label = QLabel(self.main_layout)  # Create label for notifications
        self.notif_label.setGeometry(QRect(10, 540, 620, 60))  # Set geometry for notification label
        self.notif_label.setObjectName("notif_label")  # Set object name for notification label
        self.notif_label.setDisabled(True)  # Disable notification label
        self.main_window.setCentralWidget(self.main_layout)  # Set main layout as central widget
        self.statusbar = QStatusBar(self.main_window)  # Create status bar for main window
        self.statusbar.setObjectName("statusbar")  # Set object name for status bar
        self.main_window.setStatusBar(self.statusbar)  # Set status bar for main window
        self.menubar = QMenuBar(self.main_window)  # Create menu bar for main window
        self.menubar.setGeometry(QRect(0, 0, 640, 23))  # Set geometry for menu bar
        self.menubar.setObjectName("menubar")  # Set object name for menu bar
        self.settings_menu = QMenu(self.menubar)  # Create settings menu
        self.settings_menu.setObjectName("settings_menu")  # Set object name for settings menu
        self.help_menu = QMenu(self.menubar)  # Create help menu
        self.help_menu.setObjectName("help_menu")  # Set object name for help menu
        self.about_menu = QMenu(self.menubar)  # Create about menu
        self.about_menu.setObjectName("docs_menu")  # Set object name for about menu
        self.models_menu = QMenu(self.menubar)  # Create models menu
        self.models_menu.setObjectName("models_menu")  # Set object name for models menu
        self.other_services = QMenu(self.menubar)  # Create other services menu
        self.other_services.setObjectName("other_services")  # Set object name for other services menu
        self.theme_menu = QMenu(self.menubar)  # Create theme menu
        self.theme_menu.setObjectName("theme_menu")  # Set object name for theme menu
        self.main_window.setMenuBar(self.menubar)  # Set menu bar for main window
        self.menubar.addAction(self.settings_menu.menuAction())  # Add settings menu to menu bar
        self.menubar.addAction(self.help_menu.menuAction())  # Add help menu to menu bar
        self.menubar.addAction(self.about_menu.menuAction())  # Add about menu to menu bar
        self.menubar.addAction(self.models_menu.menuAction())  # Add models menu to menu bar
        self.menubar.addAction(self.theme_menu.menuAction())  # Add theme menu to menu bar

        self.settings_action = QAction("Settings", self.main_window)  # Create action for settings
        self.docs_action = QAction("Full Documentation", self.main_window)  # Create action for documentation
        self.models_action = QAction("Explor Models", self.main_window)  # Create action for exploring models
        self.questions_action = QAction("Questions", self.main_window)  # Create action for questions
        self.support_action = QAction("Online Support", self.main_window)  # Create action for online support
        self.about_me_action = QAction("About me", self.main_window)  # Create action for about me
        self.website_action = QAction("Website", self.main_window)  # Create action for website
        self.translator_action = QAction("Translator", self.main_window)  # Create action for translator
        self.image_generator = QAction("Image Generator", self.main_window)  # Create action for image generator
        self.light_theme_action = QAction("Light theme", self.main_window)  # Create action for light theme
        self.dark_theme_action = QAction("Dark theme", self.main_window)  # Create action for dark theme
        self.theme_action = QAction("Change Theme", self.main_window)  # Create action for changing theme

        # Connect actions to their functions
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

        # Add menus to main menu
        self.models_menu.addAction(self.models_action)
        self.settings_menu.addAction(self.settings_action)
        self.help_menu.addActions([self.docs_action, self.questions_action, self.support_action])
        self.about_menu.addActions([self.about_me_action, self.website_action])
        self.other_services.addActions([self.image_generator, self.translator_action])
        self.theme_menu.addActions([self.dark_theme_action, self.light_theme_action])

        # Add actions to main menubar
        self.menubar.addAction(self.models_menu.menuAction())
        self.menubar.addAction(self.other_services.menuAction())
        self.menubar.addAction(self.settings_menu.menuAction())
        self.menubar.addAction(self.about_menu.menuAction())
        self.menubar.addAction(self.help_menu.menuAction())
        self.menubar.addAction(self.theme_menu.menuAction())


        # Set text for some widgets (some of them are default names and will be changed)
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

        # Add service_type_combobox widget (which is a combobox to select and chose service type) to the main layout
        self.service_type_combobox= QComboBox(self.main_layout)
        self.service_type_combobox.setGeometry(QRect(10, 465, 200, 30))
        self.service_type_combobox.setObjectName("service_type_combobox")
        for service_type in self.service_types: # Load the service types to the combobox
            icon = QIcon(media['service_type'][service_type.lower()])
            self.service_type_combobox.addItem(icon, service_type)
        self.service_type_combobox.setCurrentText(self.service_type.lower().capitalize())
        self.core_objects['client'].service_type = self.service_type.lower() # Set the default service type to the client object
        self.service_type_combobox.currentIndexChanged.connect(self.change_service_type)

        # Add api_key_input widget (which is a line edit to input API key) to the main layout
        self.api_key_input = QLineEdit(self.main_layout)
        self.api_key_input.setGeometry(QRect(10, 500, 200, 30))
        self.api_key_input.setObjectName("api_key_input")
        self.api_key_input.setPlaceholderText("Enter API key if needed")  # Optional placeholder text

        # Connect the button to their actions
        self.send_button.clicked.connect(self.send_prompt)
        self.new_chat_button.clicked.connect(self.create_new_chat)
        self.ping_button.clicked.connect(self.ping)
        self.api_key_input.editingFinished.connect(self.save_api_key)
        self.set_theme('read') # Read the theme from the settings and apply it

        QMetaObject.connectSlotsByName(self.main_window)

    def about_me(self):
        about_me_website = core.read_configs()['develop']['website']
        webbrowser_open(about_me_website)

    def set_theme(self, theme='read'):
        if theme == 'read':
            theme = core.read_settings()['ai']['theme'] # Read the theme from the settings
        if theme == 'dark':
            self.main_window.setStyleSheet(self.dark_theme) # Set dark theme to the main window
        else:
            self.main_window.setStyleSheet(self.light_theme) # Set light theme to the main window
            theme = 'light'
        # Read the settings and change the theme then save it.
        settings = core.read_settings()
        settings['ai']['theme'] = theme
        core.store_settings(settings)
        self.show_notif(f"Application theme set to {theme}") # Show notification about theme change

    def app_website(self):
        # Open the app website in the default web browser
        app_website = core.read_configs()['develop']['app_website']
        webbrowser_open(app_website)

    def run_translator(self):
        # Run the translator plugin in a new window
        try:
            from plugins.Translator.app import TranslatorApp
            self.translator_window = QMainWindow()
            self.translator_app = TranslatorApp()
            self.translator_app.setupUi(self.translator_window)
            self.translator_window.show()
        except Exception as e:
            # Show error in running translator if happend
            self.show_notif("Error in running translator: " + str(e), color='red', during=10)

    def destroy_notif(self):
        # Destroy the current notification label
        try:
            self.notif_label.hide()
        except: # the exception handling here is for the RuntimeError (which is happend when the widget/window is destroyed)
            pass

    def run_image_generator(self):
        # Run the image generator plugin in a new window
        try:
            from plugins.ImageGenerator.app import ImageGeneratorApp
            self.image_generator_app = ImageGeneratorApp()
            self.image_generator_app.show()
        except Exception as e:
            self.show_notif("Error in running image generator: " + str(e), color='red', during=10)

    def menu_clicked(self, action):
        # Show a message when the user clicks on a menu item which is add in new versions
        self.show_notif(f"This section [{action}] will be activate in next versions...")

    def send_prompt(self):
        # Send a prompt to the agent when the user clicks on the send button
        if not self.current_conversion_id:
            # Show error message if no chat is selected
            return self.show_notif("First start a new chat or select an existing chat on the left side.", color='red')
        
        # Set the agent status to running a task
        self.agent_status_label.setText(
            self._translate("main_window", "<font color='green'>Agent is running task...</font>"))
        self.api_key = self.api_key_input.text() # Read the api key
        self.core_objects['client'].api_key = self.api_key # Set the api key to the client object
        self.agent_status_label.update()  # Update the label immediately

        prompt = self.prompt_text_edit.toPlainText() # Read the prompt text
        self.prompt_text_edit.clear() # Clear the prompt text edit
        self.temp_prompt = prompt # store prompt in self.temp_prompt for usage in other functions/methods/objects
        self.core_objects['client'].conversion_id = self.current_conversion_id # Set the conversion id to the client object

        # Create and start the thread
        self.ai_client_thread = AiClientThread(self.core_objects['client'], prompt) # Create AiClientThread object for response the user
        self.ai_client_thread.task_completed.connect(self.on_task_completed) # Connect the task_completed event to self.task_completed method
        self.ai_client_thread.start() # Start the thread

    def on_task_completed(self, status, message):
        status = True if status == 'True' else False # store status which is show task successfully completed or not
        if not status: # if status is False (task didnt completed successfully)
            self.show_notif(message, color='red', during=8) # Show the error message as a notification
            return

        is_first_message = len(self.conversion_messages) == 0 # check if it's the first message in conversion
        if is_first_message:  # update and set conversion title if it's the first message in conversion
            title = self.temp_prompt
            if len(title) > 15:
                title = f"{title[:15]}..."  # set the first 15 characters of prompt for title of the conversion
            self.core_objects['client'].database.update_conversion(self.current_conversion_id, title) # update the conversion title in database
            self.update_chats() # Update the chats list and show them

        self.load_conversion_messages(self.current_conversion_id) # Load the conversion messages (will show response)
        self.agent_status_label.setText(
            self._translate("main_window", "<font color='blue'>Agent is waiting for task...</font>")) # Set the agent status to waiting for task

    def show_notif(self, message, during=3, color: str = 'blue', font=None):
        core.log(f"NOTIF: {message}", 'debug') # Log the notification
        settings = core.read_settings()['ai'] # Read the settings
        if settings['show_notif'] == "OFF": # If the notification type is set to OFF, return
            return
        if settings['notif_type'] == "messagebox":  # If the notification type is set to messagebox, show a message box
            # Show the notification in a message box with a color and message (show critical for red color, yellow for warning color, and anything else for info color)
            if color == 'red':
                return QMessageBox.critical(self.main_window, "NOTIF", message)
            elif color == 'yellow':
                return QMessageBox.warning(self.main_window, "NOTIF", message)
            else:
                return QMessageBox.information(self.main_window, "NOTIF", message)
        else:
            if font: # if a font is specified set the font for the notification label
                self.notif_label.setFont(font)
            else: # Make the font for the notification label (default font, bold, and not italic)
                font = QFont()
                font.setFamily("Noto Sans")
                font.setPointSize(10)
                font.setBold(True)
                self.notif_label.setFont(font) # Set the font for the notification label
            self.notif_label.setStyleSheet(
                "background-color: white; border: 1px solid black; border-radius: 10px; padding: 5px;") # Set the style for the notification label
            self.notif_label.setText(self._translate("main_window", f"<font color='{color}'>{message}</font>")) # Set the text for the notification label
            self.notif_label.setEnabled(True) # Enable the notification label
            self.notif_label.show() # Show the notification label for the specified duration
            Timer(during, self.destroy_notif).start() # Set a timer to destroy the notification label after the specified duration

    def ping(self): # Ping and show the engine is online message
        """
        This function dont check the engine status in this version
        It just shows a notification message that the engine is online

        It can uses to know the windows is working correctly or not
        """
        # Make a font to display
        font = QFont()
        font.setFamily("Noto Sans")
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(True)
        # Show a notification message that the engine is online with a bold, italic, and red font color
        self.show_notif('Engine is online!', 3, font=font)

    def create_new_chat(self):
        # Show a dialog to select a model
        dialog = ModelSelectionDialog(service_type=self.service_type)
        # If the user accepted the dialog and selected a model, get the selected model and create a new chat with it
        if dialog.exec_() == QDialog.Accepted:
            selected_model = dialog.selected_model
            # Record the new chat in the database with the selected model id
            self.core_objects['client'].database.record_conversion(title="A new chat", model_id=core.get_model_info(name=selected_model, database=self.core_objects['database'])['id'])
            # Show a notification message that a new chat has been created
            self.show_notif("new chat created, please select it if you want to send prompt", 3, color='green')
            # Update the chats list
            self.update_chats()

    def update_chats(self):
        # Destroy existing chat buttons
        for chat_obj in self.chats_buttons:
            chat_obj.deleteLater()
        self.chats_buttons.clear()  # Clear the list after destroying

        # Fetch new chats
        self.chats = self.core_objects['client'].database.get_conversions()

        # Do a for loop to create chat buttons and connect them to load messages
        for index, chat_info in enumerate(self.chats):
            chat_title = chat_info['title']
            chat_id = chat_info['id']
            chat = QPushButton(self.chats_layout_widget) # Create chats as a button
            chat.setObjectName(f"chat{index}") # Set the object name for the chat button
            self.chats_layout.addWidget(chat) # Add the chat button to the layout
            chat.setText(self._translate("main_window", str(chat_title))) # Set the text for the chat button
            func = partial(self.load_conversion_messages, chat_id) # Create a partial function to load messages when the chat button is clicked
            chat.clicked.connect(func) # Connect the chat button to its load messages
            self.chats_buttons.append(chat) # Add the chat button to the list of chat buttons

    def load_conversion_messages(self, conversion_id):
        # Clear existing messages
        while self.messages_layout.count():  # While there are items in the layout
            item = self.messages_layout.takeAt(0)  # Take the first item
            if item.widget():  # If it's a widget, delete it
                item.widget().deleteLater()  # Schedule for deletion

        # store the current conversion id in self.current_conversion_id
        self.current_conversion_id = int(conversion_id)
        # Fetch and store conversion messages in self.conversion_messages
        self.conversion_messages = self.core_objects['client'].database.get_conversion_messages(
            self.current_conversion_id)

        # Check if there is no messages in the conversion
        if not self.conversion_messages:
            no_message_label = QLabel("No messages available for this chat. start it", self.messages_widget) # Show a label if there are no messages in the conversion
            self.messages_layout.addWidget(no_message_label) # Add the label to the layout
            return

        # Do a for loop to create message labels and add them to the layout
        for message_info in self.conversion_messages:
            message_id = message_info['id']
            message_text = message_info['message']
            message_author = message_info['role']

            # Create message label
            message_label = QLabel(self.messages_widget)  # Use messages_widget as parent
            message_label.setWordWrap(True)  # Enable word wrapping
            message_label.setText(f"{message_author}: {message_text}") # Set the text for the message label with "author: message_text" format

            # Add to layout
            self.messages_layout.addWidget(message_label)

        # Add stretch at the end to push messages to the top
        self.messages_layout.addStretch()

        # Update the scroll area to ensure it displays the new messages
        self.scroll_area.update()

    def change_service_type(self, new_service_type_index):
        # Update the selected service type
        self.service_type = self.service_types[int(new_service_type_index)].lower()
        # Read the settings and update the service type in the settings dictionary
        settings = core.read_settings()
        settings['ai']['service_type'] = self.service_type
        core.store_settings(settings) # Store the updated settings
        self.show_notif(f"Service type changed to {self.service_type}") # Show a notification message about the service type change


class SettingsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Notification Settings App') # Set the window title
        self.setGeometry(100, 100, 300, 200) # Set the window size

        central_widget = QWidget() # make a central widget
        self.setCentralWidget(central_widget) # Set the widget as the central widget of the window
        layout = QVBoxLayout(central_widget) # Create a vertical layout for the central widget

        self.notification_checkbox = QCheckBox('Show Notifications') # Create a checkbox for notifications

        self.notification_type_label = QLabel('Notification Type:') # Create a label for notification type
        self.notification_type_combo = QComboBox() # Create a combo box for notification type
        self.notification_type_combo.addItems(['Label in Bottom', 'Message Box']) # Add notification types to the combo box
        self.notification_type_combo.setCurrentText('Label in Bottom' if notif_type == 'label' else 'Message Box') # Set the current text of the combo box based on the notification type

        # Read the current settings and set the checkbox and combo box accordingly
        _ = core.read_settings()['ai']
        notif_type = _['notif_type']
        is_notif_on = _['show_notif']
        self.notification_checkbox.setChecked(is_notif_on)

        # Create a save button and connect it to the save_settings function
        self.save_button = QPushButton('Save Settings')
        self.save_button.clicked.connect(self.save_settings)

        # Add the widgets and layout to the central widget
        layout.addWidget(self.notification_checkbox)
        layout.addWidget(self.notification_type_label)
        layout.addWidget(self.notification_type_combo)
        layout.addWidget(self.save_button)

    def save_settings(self):
        # Get the current status and notification type of the checkbox and combo box, and store them in the settings dictionary
        show_notifications = self.notification_checkbox.isChecked()
        notification_type = self.notification_type_combo.currentText()

        status = "ON" if show_notifications else "OFF"
        notif_type = "label" if notification_type == 'Label in Bottom' else 'messagebox'
        settings = core.read_settings()
        settings['ai']['notif_type'] = notif_type
        settings['ai']['show_notif'] = status
        core.store_settings(settings)
        QMessageBox.information(self, "success", "Settings saved!") # Show a success message when the settings are saved


def run_gui():
    """
    This function runs the GUI application
    it calls from the main.py or when user run this file
    """
    app = QApplication(sys.argv) # Create a QApplication instance
    main_window = QMainWindow() # Create a main window
    ui = GUI() # Create an instance of the GUI class
    ui.setupUi(main_window) # Setup the GUI with the main window
    main_window.show() # Show the main window
    sys.exit(app.exec_()) # Exit the application when the main window is closed


if __name__ == "__main__":
    run_gui() # Run the GUI application when user run this file
