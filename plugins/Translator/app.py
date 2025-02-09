# Import PyQt5 widgets, import widgets instead whole of the moudel for optimizing
from PyQt5.QtCore import QRect, Qt, QMetaObject, QCoreApplication
from PyQt5.QtGui import QFont, QCursor, QIcon # Importing font and icon classes from PyQt5
from typing import Any
from PyQt5.QtWidgets import QMainWindow, QApplication, QTextEdit, QPushButton, QComboBox, QMessageBox, QWidget, QVBoxLayout, QLayout, QHBoxLayout, QLabel # Importing necessary PyQt5 widgets
from googletrans import Translator, LANGUAGES  # Import Google Translate API, Just 3.1.0a0 version works correctly.
import sys, core # Import core and system moudel
import pyperclip  # Import pyperclip for clipboard operations


# Define the main UI class for the Translator application
class TranslatorApp:
    def __init__(self):
        # Read the settings from the file and store them in the self.settings dictionary
        self.settings = core.read_settings()['translator']
        # Store the theme in self.current_theme
        self.current_theme = self.settings['theme']
        # Store the source and dest language in variables
        self.src_lang = self.settings['src']
        self.dest_lang = self.settings['dest']
        # Light theme stylesheet
        self.light_theme = """
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
        # Dark theme stylesheet
        self.dark_theme = """
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

    # Method to get a sorted list of languages for the translator
    def get_languages(self):
        language_list = list(LANGUAGES.values())
        language_list.sort()
        sort_language_list = ['english', 'persian']  # put English and Persian in the first of the list for easy access
        for lang in language_list:
            if lang not in sort_language_list:
                sort_language_list.append(lang)
        return sort_language_list

    # Method to toggle between light and dark themes
    def toggle_theme(self):
        if self.current_theme == "light":
            self.main_window.setStyleSheet(self.dark_theme)
            self.theme_btn.setText("Light Theme")
            self.current_theme = "dark"
        else:
            self.main_window.setStyleSheet(self.light_theme)
            self.theme_btn.setText("Dark Theme")
            self.current_theme = "light"
        self.save_settings()

    def change_src_lang(self, new_src_lang):
        self.src_lang = TranslatorApp.find_key_by_value(self.languages, new_src_lang)
        self.save_settings()
        core.log(f"src_lang set to {self.src_lang}")

    def change_dest_lang(self, new_dest_lang):
        self.dest_lang = TranslatorApp.find_key_by_value(self.languages, new_dest_lang)
        self.save_settings()
        core.log(f"dest_lang set to {self.dest_lang}")

    @staticmethod
    def find_key_by_value(dictionary: dict, value: Any):
        core.log(f"find_key_by_value for {value}", 'debug')
        for key, val in dictionary.items():
            if val == value:
                return key
        core.log("Key not found", 'error')

    def save_settings(self):
        self.settings = core.read_settings()
        self.settings['translator']['src'] = self.src_lang
        self.settings['translator']['dest'] = self.dest_lang
        self.settings['translator']['theme'] = self.current_theme
        core.store_settings(self.settings)
        self.src_lang = self.settings['translator']['src']
        self.dest_lang = self.settings['translator']['dest']
        core.log(f"Settings -> src:{self.src_lang},dest:{self.dest_lang},theme:{self.current_theme}", 'debug')

    # Method to set up the UI components
    def setupUi(self, TranslatorWindow):
        media = core.list_media()
        TranslatorWindow.setWindowIcon(QIcon(media['translator']['icon']))
        TranslatorWindow.setObjectName("TranslatorWindow")
        self.main_window = TranslatorWindow
        self.main_window.setFixedSize(692, 333)  # Set fixed size for the main window
        self.centralwidget = QWidget(TranslatorWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Set up source text container
        self.source_text_container = QWidget(self.centralwidget)
        self.source_text_container.setGeometry(QRect(9, 20, 241, 171))
        self.source_text_container.setObjectName("source_text_container")
        self.verticalLayout = QVBoxLayout(self.source_text_container)
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.input_text = QTextEdit(self.source_text_container)
        self.input_text.setObjectName("input_text")
        self.verticalLayout.addWidget(self.input_text)

        # Set up paste button
        self.paste_btn = QPushButton(self.source_text_container)
        self.paste_btn.setFixedHeight(35)
        font = QFont()
        font.setFamily("Carlito")
        font.setBold(True)
        font.setWeight(75)
        self.paste_btn.setFont(font)
        self.paste_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.paste_btn.setObjectName("paste_btn")
        self.verticalLayout.addWidget(self.paste_btn)

        # Add theme toggle button
        self.theme_btn = QPushButton(self.centralwidget)
        self.theme_btn.setGeometry(QRect(300, 200, 87, 27))
        self.theme_btn.setFont(font)
        self.theme_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.theme_btn.setObjectName("theme_btn")
        self.theme_btn.clicked.connect(self.toggle_theme)

        # Set up footer container
        self.footer_container = QWidget(self.centralwidget)
        self.footer_container.setGeometry(QRect(10, 300, 671, 31))
        self.footer_container.setObjectName("footer_container")
        self.horizontalLayout_2 = QHBoxLayout(self.footer_container)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.author_label = QLabel(self.footer_container)
        font = QFont()
        font.setFamily("Carlito")
        font.setBold(True)
        self.author_label.setFont(font)
        self.author_label.setObjectName("author_label")
        self.horizontalLayout_2.addWidget(self.author_label)
        self.version_label = QLabel(self.footer_container)
        font = QFont()
        font.setFamily("Carlito")
        font.setBold(True)
        self.version_label.setFont(font)
        self.version_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.version_label.setObjectName("version_label")
        self.horizontalLayout_2.addWidget(self.version_label)

        # Set up target text container
        self.target_text_container = QWidget(self.centralwidget)
        self.target_text_container.setGeometry(QRect(440, 20, 241, 171))
        self.target_text_container.setObjectName("target_text_container")
        self.verticalLayout_2 = QVBoxLayout(self.target_text_container)
        self.verticalLayout_2.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.output_text = QTextEdit(self.target_text_container)
        self.output_text.setObjectName("output_text")
        self.verticalLayout_2.addWidget(self.output_text)

        # Set up copy button
        self.copy_btn = QPushButton(self.target_text_container)
        self.copy_btn.setFixedHeight(35)
        font = QFont()
        font.setFamily("Carlito")
        font.setBold(True)
        font.setWeight(75)
        self.copy_btn.setFont(font)
        self.copy_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.copy_btn.setObjectName("copy_btn")
        self.verticalLayout_2.addWidget(self.copy_btn)

        # Set up translate and clear buttons
        self.translate_btn = QPushButton(self.centralwidget)
        self.translate_btn.setGeometry(QRect(280, 70, 131, 51))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.translate_btn.setFont(font)
        self.translate_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.translate_btn.setObjectName("translate_btn")
        self.clear_btn = QPushButton(self.centralwidget)
        self.clear_btn.setGeometry(QRect(300, 150, 87, 27))
        font.setBold(True)
        font.setWeight(75)
        self.clear_btn.setFont(font)
        self.clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.clear_btn.setObjectName("clear_btn")

        # Set up language selection container
        self.language_selection_container = QWidget(self.centralwidget)
        self.language_selection_container.setGeometry(QRect(10, 240, 668, 41))
        self.language_selection_container.setObjectName("language_selection_container")
        self.horizontalLayout = QHBoxLayout(self.language_selection_container)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.source_language_combo = QComboBox(self.language_selection_container)
        self.source_language_combo.setObjectName("source_language_combo")
        self.source_language_combo.setGeometry(QRect(0, 0, 241, 30))
        font_combobox = QFont()
        font_combobox.setPointSize(12)
        font_combobox.setBold(True)
        font_combobox.setWeight(75)
        self.source_language_combo.setFont(font_combobox)
        self.horizontalLayout.addWidget(self.source_language_combo)
        self.to_label = QLabel(self.language_selection_container)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.to_label.setFont(font)
        self.to_label.setAlignment(Qt.AlignCenter)
        self.to_label.setObjectName("to_label")
        self.horizontalLayout.addWidget(self.to_label)
        self.target_language_combo = QComboBox(self.language_selection_container)
        self.target_language_combo.setObjectName("target_language_combo")
        self.target_language_combo.setGeometry(QRect(0, 0, 241, 30))
        self.target_language_combo.setFont(font_combobox)
        self.horizontalLayout.addWidget(self.target_language_combo)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(2, 1)
        TranslatorWindow.setCentralWidget(self.centralwidget)

        # Call method to set text for widgets
        self.retranslateUi(TranslatorWindow)
        QMetaObject.connectSlotsByName(TranslatorWindow)

        # Find and assign UI components
        self.input_text = self.main_window.findChild(QTextEdit, "input_text")
        self.output_text = self.main_window.findChild(QTextEdit, "output_text")
        self.translate_btn = self.main_window.findChild(QPushButton, "translate_btn")
        self.clear_btn = self.main_window.findChild(QPushButton, "clear_btn")
        self.paste_btn = self.main_window.findChild(QPushButton, "paste_btn")
        self.copy_btn = self.main_window.findChild(QPushButton, "copy_btn")
        self.source_language_combo = self.main_window.findChild(QComboBox, "source_language_combo")
        self.target_language_combo = self.main_window.findChild(QComboBox, "target_language_combo")

        # initalize values for language selection combo boxes
        self.languages = LANGUAGES
        self.languages['auto'] = 'auto detect'
        self.language_list = self.get_languages()
        from_comb_items = ['auto detect']
        from_comb_items.extend(self.language_list)
        self.source_language_combo.addItems(from_comb_items)
        self.target_language_combo.addItems(self.language_list)

        self.source_language_combo.setCurrentText(self.languages[self.src_lang])
        self.target_language_combo.setCurrentText(self.languages[self.dest_lang])

        # Connect buttons to their methods
        self.target_language_combo.currentTextChanged.connect(self.change_dest_lang)
        self.source_language_combo.currentTextChanged.connect(self.change_src_lang)
        self.translate_btn.clicked.connect(self.translate)
        self.clear_btn.clicked.connect(self.clear)
        self.paste_btn.clicked.connect(self.paste)
        self.copy_btn.clicked.connect(self.copy)

        # Apply initial theme
        if self.current_theme == "dark":
            self.main_window.setStyleSheet(self.dark_theme)
            self.theme_btn.setText("Light Theme")
        elif self.current_theme == 'light':
            self.main_window.setStyleSheet(self.light_theme)
            self.theme_btn.setText("Dark Theme")

        # Show the main window
        self.main_window.show()

    # Method to set text for widgets
    def retranslateUi(self, TranslatorWindow):
        _translate = QCoreApplication.translate
        TranslatorWindow.setWindowTitle(_translate("TranslatorWindow", "Translator App"))
        self.paste_btn.setText(_translate("TranslatorWindow", "Paste"))
        self.author_label.setText(_translate("TranslatorWindow", "By Abolfazl Eskandari"))
        self.version_label.setText(_translate("TranslatorWindow", "V 0.1"))
        self.copy_btn.setText(_translate("TranslatorWindow", "Copy"))
        self.translate_btn.setText(_translate("TranslatorWindow", "Translate"))
        self.clear_btn.setText(_translate("TranslatorWindow", "Clear"))
        self.to_label.setText(_translate("TranslatorWindow", "To"))

    # Method for translating text
    def translate(self):
        try:
            from_lang_key = None
            to_lang_key = None
            for key, value in self.languages.items():
                if (value == self.source_language_combo.currentText()):
                    from_lang_key = key

            for key, value in self.languages.items():
                if (value == self.target_language_combo.currentText()):
                    to_lang_key = key
            if not from_lang_key or self.source_language_combo.currentText() == 'auto detect':
                from_lang_key = 'auto'

            text = self.input_text.toPlainText()

            translator_obj = Translator() # Create a Translator object
            translated_text = translator_obj.translate(text, src=from_lang_key, dest=to_lang_key) # Translate the text

            self.output_text.setText(str(translated_text.text)) # Write translated text in output text edit
            self.src_lang = translated_text.src # Store the source language in self.src_lang
            self.dest_lang = translated_text.dest # Store the dest language in self.dest_lang
            self.save_settings() # Save the source language and dest language in settings

        except Exception as e: # Handle the exception
            QMessageBox.critical(self.main_window, "Translator", str(e)) # Show the error in a message box

    # Method to clear the input and output text widgets
    def clear(self):
        self.input_text.setText("")
        self.output_text.setText("")

    # Method to copy the output text to clipboard
    def copy(self):
        pyperclip.copy(self.output_text.toPlainText())
        return QMessageBox.information(self.main_window, "Translator", "copied to clipboard.")

    # Method to paste text from clipboard into the input text widget
    def paste(self):
        clipboard = pyperclip.paste()
        if not clipboard:
            return QMessageBox.warning(self.main_window, "Translator", "You don't have anything in your clipboard!")
        else:
            self.input_text.setText(clipboard)
            return QMessageBox.information(self.main_window, "Translator", "Clipboard pasted.")


# Run application if it's the main module for example if it's running by python3 app.py
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    translator = TranslatorApp()
    translator.setupUi(window)
    window.show()
    exit(app.exec_())
