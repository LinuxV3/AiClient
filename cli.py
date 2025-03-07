import os, platform, threading, time, sys, shutil, textwrap
import core
from logger import log
from rich.console import Console
from tqdm import tqdm
from pick import pick
from functools import partial


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

    def run(self):
        if '--ask' in self.args:
            prompt = self.get_prompt()
            if '--model' in self.args:
                model = self.args[self.args.index('--model') + 1].strip()
            else:
                model = self.choice_model(self.models)
            self.ask(prompt, model)
            exit()
        self.loop()
    
    def show_welcome(self):
        #self.clear()
        self.print_title("Welcome to the AI Assistant!")
    
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
                    if prompt.lower() in ['clear', 'cls']:
                        self.clear()
                        continue
                    model = self.choice_model(self.models)
                    if model == self.back_option:
                        break
                    self.ask(prompt, model)
            elif choice == 'Exit' or choice.lower() in ['q', 'exit']:
                self.print("Exiting...")
                exit()
    
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
        self.print(self.console.rule())
    
    def print_title(self, title: str):
        self.print(self.console.rule(title))
    
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
                    return

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
        self.took_time = int(self.end_time - self.start_time)
        success = response[0]
        status = "Success" if success else "Failed"
        if self.show_progress_time:
            self.print(f"{status}, Took {self.took_time}ms [Service: {self.client.service_type}, AI Model: {model}]")
        self.print_pretty(response[1])


def run_cli():
    cli = CLI(sys.argv)
    cli.run()


if __name__ == '__main__':
    run_cli()
