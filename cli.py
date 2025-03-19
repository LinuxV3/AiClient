import os, platform, threading, time, sys, shutil, textwrap, signal
from functools import partial
import core
from logger import log
libs = {'rich': 'rich', 'tqdm': 'tqdm', 'pick': 'pick', 'googletrans': 'googletrans==3.1.0a0'}
try:
    from rich.console import Console
    from tqdm import tqdm
    from pick import pick
    from googletrans import Translator, LANGUAGES
except ImportError as e:
    log(f"Missing required library: {e}", 'error')
    for name_to_import, name_to_install in libs.items():
        core.install_package(package_name=None, name_to_import=name_to_import, name_to_install=name_to_install)
    try:
        from rich.console import Console
        from tqdm import tqdm
        from pick import pick
        from googletrans import Translator, LANGUAGES
    except Exception as e:
        log(f"Another exception during import required libraries: {e}", 'error')
        log("Install libraries manually")
        exit()


def exit_signal_handler(*args, **kwargs):
    os.system("cls") if platform.system() == 'Windows' else os.system('clear')
    print("Exiting...")
    exit()


signal.signal(signal.SIGINT, exit_signal_handler)


class CLI:
    def __init__(self, args=None):
        self.args = args or []
        self.console = Console()
        self.back_option = ' *Back* '
        self.services = ['g4f', 'local']
        self.service_type = 'g4f'
        self.model = 'g4f-4o-mini'
        self.client = core.AiClient()
        self.welcome = True
        self.client.init(ignore_database=True)
        self.models = ['gpt-4o-mini', 'gpt-4o']
        self.db = self.client.database
        self._print = print
        self.took_time = 0
        self.show_progress_time = False
        self.stream = True
        self.langs = [self.back_option, 'auto', 'en', 'fa']
        for lang in LANGUAGES:
            if lang not in self.langs:
                self.langs.append(lang)
        self.dest_langs = [self.back_option]
        self.dest_langs.extend(self.langs[2:])
        self.image_models = ['sdxl',
                            'sd-3',
                            'playground-v2.5',
                            'flux',
                            'flux-pro',
                            'flux-realism',
                            'flux-cablyai',
                            'flux-anime',
                            'flux-3d',
                            'flux-disney',
                            'flux-pixel',
                            'flux-4o',
                            'dall-e-3',
                            'midjourney',
                            'any-dark']

    def run(self):
        if '--ask' in self.args:
            prompt = self.get_prompt()
            if '--model' in self.args:
                model = self.args[self.args.index('--model') + 1].strip()
            else:
                model = self.choice_model(self.models)
            self.ask(prompt, model)
            self.exit()
        self.loop()
    
    def show_welcome(self):
        self.clear()
        self.print_title("Welcome to the AI Assistant!")
    
    exit = exit_signal_handler

    def proccess_command(self, command):
        if command.lower() in ['clear', 'cls']:
            self.clear()
            return True

    def loop(self):
        if self.welcome:
            self.show_welcome()
            self.welcome = False
        while True:
            choice = self.get_input(use_pick=True, text_input=False, options=['Ask', 'Translator', 'Image Generator', 'About us', 'Exit'])
            if choice == 'Ask':
                self.print_title("Enter your prompt then choose the AI model")
                self.print_title("Type 'q' or 'exit' to exit")
                while True:
                    prompt = self.get_prompt()
                    if not prompt:
                        continue
                    if prompt.lower() in ['q', 'exit']:
                        break
                    if self.proccess_command(prompt):
                        continue
                    model = self.choice_model(self.models)
                    if model == self.back_option:
                        break
                    self.ask(prompt, model)
            elif choice == 'Translator':
                self.translator_loop()
            elif choice == 'Image Generator':
                self.image_generator_loop()
            elif choice == 'About us':
                self.about_info()
            elif choice == 'Exit' or choice.lower() in ['q', 'exit']:
                self.exit()
    
    def image_generator_loop(self):
        self.clear()
        self.print_title("Welcome to Image Generator App!")
        try:
            from plugins.ImageGenerator.app import generate_image_
        except ImportError:
            self.print("Failed to import Image Generator core from the plugin.")
            return
        while True:
            prompt = self.get_prompt()
            if prompt.lower() in ['q', 'exit']:
                break
            if self.proccess_command(prompt):
                continue
            ai_model = self.get_input(text_input=False, use_pick=True, options=self.image_models, prompt='Choice AI model:')
            result = generate_image_(prompt=prompt, model=ai_model, service_type='g4f')
            success = result[0]
            if not success:
                self.print(f"An error happend, {result[1]}")
                continue
            images_url = list(set(result[1]))
            if not images_url:
                self.print("There is no image to show.")
                continue
            images_url_str = " > " + '\n> '.join(images_url)
            self.print(images_url_str)
            self.print("Above urls are the images")
            is_download_images = self.get_input(text_input=True, use_pick=False, prompt="Do you want to download them ? [N or y]: ")
            if not is_download_images:
                is_download_images = 'n'
            if is_download_images == 'n':
                is_download_images = False
            elif is_download_images == 'y':
                is_download_images = True
            else:
                self.print("Inavlid input.")
                continue
            if not is_download_images:
                continue
            try:
                images_path = self.download_files(images_url, use_api=True)
                images_path_str = " > " + '\n> '.join(images_path)
                self.print("Images downloaded successfully.")
                self.print(images_path_str)
            except Exception as e:
                self.print(f"Error in downloading images: {e}")

                raise e
                continue
        self.clear()
    
    def download_files(self, images_url, use_api=False, just_one=False):
        save_dir = "output/"
        os.makedirs(save_dir, exist_ok=True)
        images_path = []
        for file_url in images_url:
            try:
                image_name = f"image_{str(int(time.time()))[-3:]}.png"
                image_path = os.path.join(save_dir, image_name)
                if use_api:
                    api_endpoint = "https://aiclient.pythonanywhere.com/image_upload"
                    json_content = {'url': file_url}
                    response = core.requests.get(api_endpoint, json=json_content, stream=True)
                else:
                    response = core.requests.get(file_url, stream=True)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                with open(image_path, 'wb') as f:
                    downloaded_size = 0
                    with tqdm(total_size) as progress:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            progress.update(downloaded_size)
                images_path.append(image_path)
            except Exception as e:
                try:
                    os.remove(image_path)
                except:
                    pass
                if use_api and not just_one:
                    images_path.append(self.download_files([file_url], use_api=False, just_one=True)[0])
                else:
                    raise e
        return images_path
    
    def clear(self):
        os.system("cls") if platform.system() == 'Windows' else os.system('clear')
        self.conversion_messages = []
    
    def get_input(self, text_input: bool=True, use_pick: bool=False, options: list=None, prompt: str="Choice:"):
        if options and use_pick and prompt:
            selected, index = pick(options, prompt, indicator=" > ")
            return selected
        elif text_input and prompt:
            return self.console.input(prompt)
        else:
            raise ValueError("Bad input")
    
    def print(self, prompt: str, **kwargs):
        self.console.print(prompt, **kwargs)
    
    def print_sep(self):
        self.console.rule()
    
    def print_title(self, title: str):
        self.console.rule(title)
    
    def add_back_option(self, the_list: list):
        lst = [self.back_option]
        lst.extend(the_list)
        return lst
    
    def choice_model(self, models: list):
        return self.get_input(text_input=False, use_pick=True, options=self.add_back_option(models), prompt="=> Choice the AI model from the list bellow: ")

    def choice_service(self):
        return self.get_input(text_input=False, use_pick=True, options=self.add_back_option(self.services), prompt="=> Choice the AI model from the list bellow: ")
    
    def get_prompt(self):
        return self.get_input(prompt=" > ", use_pick=False, text_input=True)

    def show_progress_bar(self):
        symbols = ['/', '-', '\\', '|']
        while True:
            for symbol in symbols:
                if not self.progress_event.is_set():
                    self._print('\r', end='')  # Ensure immediate output
                    self._print(f"Progress is doing {symbol}", end='')
                    time.sleep(0.5)
                else:
                    self._print('\r', end='')
                    self._print(" " * 50, end='')
                    self._print('\r', end='')
                    return

    def translate_text(self, text, src_lang, dest_lang):
        self.translator_obj = Translator() # Create a Translator object
        self.translated_text = self.translator_obj.translate(text, src=src_lang, dest=dest_lang) # Translate the text
        self.progress_event.set()
        return self.translated_text.text

    def translator_loop(self):
        self.clear()
        self.print_title("Welcome to Translator App!")
        while True:
            text = self.get_prompt()
            if text.lower() in ['q', 'exit']:
                break
            if self.proccess_command(text):
                continue
            src_lang = self.get_input(text_input=False, use_pick=True, options=self.langs, prompt="Choice source language:")
            if src_lang == self.back_option:
                continue
            dest_lang = self.get_input(text_input=False, use_pick=True, options=self.dest_langs, prompt="Choice dest language:")
            if dest_lang == self.back_option:
                continue
            trans_func = partial(self.translate_text, text, src_lang, dest_lang)
            self.progress_event = threading.Event()
            trans_thread = threading.Thread(target=trans_func, args=())
            progress_thread = threading.Thread(target=self.show_progress_bar)
            trans_thread.start()
            progress_thread.start()
            trans_thread.join()
            progress_thread.join()
            self.progress_event.set()
            self.print_pretty(self.translated_text.text)
        self.clear()

    def print_pretty(self, text):
        terminal_width = shutil.get_terminal_size().columns - 6
        lines = text.splitlines()
        for line in lines:
            wrapper = textwrap.TextWrapper(width=terminal_width, break_long_words=False, replace_whitespace=False)            
            wrapped_lines = wrapper.wrap(line)
            indented_lines = []
            for wrapped_line in wrapped_lines:
                if wrapped_lines.index(wrapped_line) == 0 and lines.index(line) == 0:
                    indented_lines.append(' > ' + wrapped_line + '   ')
                else:
                    indented_lines.append('   ' + wrapped_line + '   ')
            for indented_line in indented_lines:
                self.print(indented_line)


    def ask(self, prompt, model):
        self.start_time = int(time.time() * 1000)
        self.client.model = model
        self.client.stream = self.stream
        self.progress_event = threading.Event()
        self.request_thread = threading.Thread(target=partial(self.client.ask, prompt, self.progress_event.set))
        self.progress_thread = threading.Thread(target=self.show_progress_bar)
        self.request_thread.start()
        self.progress_thread.start()
        self.request_thread.join()
        self.progress_thread.join()
        self.progress_event.set()
        response = self.client.response
        self.end_time = int(time.time() * 1000)
        if not self.stream:
            self.took_time = int(self.end_time - self.start_time)
            success = response[0]
            status = "Success" if success else "Failed"
            if self.show_progress_time:
                self.print(f"{status}, Took {self.took_time}ms [Service: {self.client.service_type}, AI Model: {model}]")
        if self.stream:
            self.print(" > ", end='')
            for chunk in response[1]:
                if chunk.choices[0].delta.content:
                    r = chunk.choices[0].delta.content or ""
                    for i in r:
                        print(i, end='', flush=True)
                        time.sleep(0.009)
            self.print()
            self.took_time = int(self.end_time - self.start_time)
            success = response[0]
            status = "Success" if success else "Failed"
            if self.show_progress_time:
                self.print(f"{status}, Took {self.took_time}ms [Service: {self.client.service_type}, AI Model: {model}]")
        else:
            self.print_pretty(response[1])


def run_cli():
    cli = CLI(sys.argv)
    cli.run()


if __name__ == '__main__':
    run_cli()
