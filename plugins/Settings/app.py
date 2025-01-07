import os
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget, QGroupBox,
    QFormLayout, QLineEdit, QComboBox, QPushButton, QListWidget,
    QMessageBox
)
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import threading


titles = {"AI Client": 'ai',
          "Image Generator": 'image',
          "Translator": 'translator'}
main_app_path = "/home/linuxer/Desktop/project/ai_client/"
storage = os.path.join(main_app_path, "storage")
configs_file_path = os.path.join(storage, 'json', "configs.json")
apps_main_path = os.path.join(main_app_path, "plugins/")
apps_path = {"ai": main_app_path,
             "image": os.path.join(apps_main_path, 'ImageGenerator'),
             "translator": os.path.join(apps_main_path, 'Translator')}
base_settings_file_name = os.path.join(storage, "base_settings")


class FileDownloaderApp:
    def __init__(self, master, download_dict):
        self.master = master
        self.download_dict = download_dict
        master.title("Source Downloader")
        self.label = tk.Label(master, text="Download Files")
        self.label.pack()

        self.url_label = tk.Label(master, text="URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.pack()
        self.path_label = tk.Label(master, text="Save Path:")
        self.path_label.pack()
        self.path_entry = tk.Entry(master, width=50)
        self.path_entry.pack()
        self.add_button = tk.Button(master, text="Add to Download List (Not recommended)", command=self.add_to_download_dict)
        self.add_button.pack()

        self.download_button = tk.Button(master, text="Download", command=self.start_download)
        self.download_button.pack()
        self.status_text = tk.Text(master, height=10, width=50)
        self.status_text.pack()
        self.progress = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")
        self.progress.pack()

    def add_to_download_dict(self):
        url = self.url_entry.get()
        save_path = self.path_entry.get()
        if url and save_path:
            self.download_dict[url] = save_path
            self.status_text.insert(tk.END, f"Added: {url} -> {save_path}\n")
            self.url_entry.delete(0, tk.END)  # Clear the URL entry
            self.path_entry.delete(0, tk.END)  # Clear the path entry
        else:
            messagebox.showwarning("Input Error", "Please enter both URL and Save Path.")

    def start_download(self):
        if not self.download_dict:
            messagebox.showwarning("Download Error", "No files to download. Please add files to the list.")
            return
        self.path_label.destroy()
        self.path_entry.destroy()
        self.url_label.destroy()
        self.url_entry.destroy()
        self.add_button.destroy()

        self.status_text.delete(1.0, tk.END)  # Clear previous status
        self.progress['value'] = 0  # Reset progress bar
        self.progress['maximum'] = len(self.download_dict)  # Set maximum value for progress bar
        self.status_text.insert(tk.END, "Starting downloads...\n")
        threading.Thread(target=self.download_files).start()  # Start download in a new thread

    def download_files(self):
        for url, save_path in self.download_dict.items():
            try:
                self.status_text.insert(tk.END, f"Downloading {url}...\n")
                response = requests.get(url, stream=True)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                with open(save_path, 'wb') as f:
                    downloaded_size = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        self.update_progress(downloaded_size, total_size)

                self.status_text.insert(tk.END, f"Downloaded {url} to {save_path}\n")
            except Exception as e:
                self.status_text.insert(tk.END, f"Failed to download {url}: {e}\n")

        self.status_text.insert(tk.END, "All downloads completed.\n")
        self.progress['value'] = self.progress['maximum']  # Set progress to maximum
        messagebox.showinfo("Download Complete", "Download Complete")

    def update_progress(self, downloaded_size, total_size):
        if total_size > 0:
            progress_percentage = (downloaded_size / total_size) * self.progress['maximum']
            self.progress['value'] = progress_percentage
            self.master.update_idletasks()


class Server:
    def __init__(self, description, url, server_type, key):
        self.description = description
        self.url = url
        self.server_type = server_type
        self.key = key

    def to_dict(self):
        return {
            "description": self.description,
            "url": self.url,
            "type": self.server_type,
            "key": self.key
        }
    def __repr__(self):
        return f"Server;url={self.url},type={self.server_type},key={self.key}"

class SettingsOptions(QWidget):
    def __init__(self, title):
        super().__init__()
        self.app_name = titles[title]
        self.app_path = apps_path[self.app_name]
        self.app_base_settings = os.path.join(base_settings_file_name, f"{self.app_name}.json")

        self.setWindowTitle(title)
        self.servers = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.server_list = QListWidget()
        self.layout.addWidget(self.server_list)

        self.form_layout = QFormLayout()
        self.description_input = QLineEdit()
        self.url_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["sample_json", "default_g4f"])
        self.key_input = QLineEdit()

        self.form_layout.addRow("Description:", self.description_input)
        self.form_layout.addRow("URL:", self.url_input)
        self.form_layout.addRow("Type:", self.type_input)
        self.form_layout.addRow("Key:", self.key_input)

        self.layout.addLayout(self.form_layout)

        self.add_button = QPushButton("Add Server")
        self.add_button.clicked.connect(self.add_server)
        self.layout.addWidget(self.add_button)

        self.import_button = QPushButton("Import Server from Clipboard")
        self.import_button.clicked.connect(self.import_server_from_clipboard)
        self.layout.addWidget(self.import_button)

        self.server_list.itemClicked.connect(self.load_server)

        # Reset section
        self.reset_group = QGroupBox("Reset")
        self.reset_layout = QVBoxLayout()

        self.reset_all_button = QPushButton("Reset All Settings")
        self.reset_all_button.clicked.connect(self.reset_all_settings)
        self.reset_layout.addWidget(self.reset_all_button)

        self.download_sources_button = QPushButton("Download All Sources")
        self.download_sources_button.clicked.connect(self.download_all_sources)
        self.reset_layout.addWidget(self.download_sources_button)

        self.reinstall_app_button = QPushButton("Reinstall App")
        self.reinstall_app_button.clicked.connect(self.reinstall_app)
        self.reset_layout.addWidget(self.reinstall_app_button)

        self.reset_group.setLayout(self.reset_layout)
        self.layout.addWidget(self.reset_group)

    def add_server(self):
        description = self.description_input.text()
        url = self.url_input.text()
        server_type = self.type_input.currentText()
        key = self.key_input.text()

        if not description or not url or not key:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        server = Server(description, url, server_type, key)
        self.servers.append(server)
        self.update_server_list()
        self.clear_inputs()

    def get_settings(self):
        with open(os.path.join(self.app_path, "settings.json")) as f:
            data = json.load(f)
        return data

    def reset_settings(self):
        with open(self.app_base_settings) as file:
            base_settings = json.load(file)
        self.save_settings(base_settings)

    def save_server_list(self, servers):
        settings = self.get_settings()
        settings["servers"] = servers
        self.save_settings(settings)

    def save_settings(self, settings):
        with open(os.path.join(self.app_path, 'settings.json'), "w") as file:
            json.dump(settings, file)

    def update_server_list(self):
        self.server_list.clear()
        for server in self.servers:
            self.server_list.addItem(server.description)
        self.save_server_list(self.servers)

    def load_server(self, item):
        index = self.server_list.row(item)
        server = self.servers[index]
        self.description_input.setText(server.description)
        self.url_input.setText(server.url)
        self.type_input.setCurrentText(server.server_type)
        self.key_input.setText(server.key)

    def clear_inputs(self):
        self.description_input.clear()
        self.url_input.clear()
        self.type_input.setCurrentIndex(0)
        self.key_input.clear()

    def import_server_from_clipboard(self):
        clipboard = QApplication.clipboard()
        data = clipboard.text()
        try:
            server_data = json.loads(data)
            server = Server(
                description=server_data["description"],
                url=server_data["url"],
                server_type=server_data["type"],
                key=server_data["key"]
            )
            self.servers.append(server)
            self.update_server_list()
        except (json.JSONDecodeError, KeyError):
            QMessageBox.warning(self, "Import Error", "Invalid server data in clipboard.")

    def reset_all_settings(self):
        reply = QMessageBox.question(self, 'Reset All Settings',
                                     'Are you sure you want to reset all settings?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No )
        if reply == QMessageBox.Yes:
            self.reset_settings()
            self.update_server_list()
            QMessageBox.information(self, "Reset", "All settings have been reset.")

    def download_all_sources(self):
        with open(configs_file_path, 'rt') as file:
            configs = json.load(file)
        app_sources_to_download = configs["sources"][self.app_name]
        root = tk.Tk()
        app = FileDownloaderApp(root, app_sources_to_download)
        root.mainloop()

    def reinstall_app(self):
        QMessageBox.information(self, "Reinstall App", "Reinstalling the app... (This is a placeholder action)")

class SettingsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings App")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.ai_client_manager = SettingsOptions("AI Client")
        self.image_generator_manager = SettingsOptions("Image Generator")
        self.translator_manager = SettingsOptions("Translator")

        self.tabs.addTab(self.ai_client_manager, "AiClient")
        self.tabs.addTab(self.image_generator_manager, "ImageGenerator")
        self.tabs.addTab(self.translator_manager, "Translator")


def run():
    app = QApplication(sys.argv)
    settings_app = SettingsApp()
    settings_app.resize(400, 300)
    settings_app.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
