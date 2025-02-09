from typing import Any
from requests.api import request as request_api
from g4f import Client as G4fClient
from g4f.api import run_api
import urllib.parse
import sqlite3, os, sys, shutil, json, requests
from threading import Thread
from logger import log


def request__(method: str, url: str, **kwargs) -> Any:
    # This function requests to a web url address
    log(f"Try send request to {url}", "debug")
    response = request_api(method, url)
    log(f"Request sent with {response.status_code} status code", "debug")
    return response


def get_file_url(file_name: str) -> str: # make the url of downloading the file
    return urllib.parse.urljoin(server_url, 'api/files/' + file_name)


built_databases = [] # This list contains the databases which the base queries executed on it
server_url = 'http://aiclient.pythonanywhere.com/' # Its a free host from https://pythonanywhere.com
configs_file_path = "storage/json/configs.json" # Configs file is a json file which contains settings, models, and other values

"""
def get_configs(slices):
    configs = read_configs()
    value = configs
    for slice in slices:
        value = value[slice]
    return value""" # unusefull


def read_configs() -> dict:
    """Reading the configs
    This functions read the configs from the configs file which is stored is `configs_file_path` var

    Returns:
        Dict: configs content
    """
    try:
        with open(configs_file_path, 'rt') as file:
            configs = json.load(file)
        log('configs file read')
        return configs
    except Exception as e:
        log(f"Error reading configs file: {e}", log_type='Error')
        file_content = get_file(get_file_url('configs.json'))
        with open(configs_file_path, 'wb') as file:
            file.write(file_content)
        return read_configs()


def get_available_models(service_type: str) -> list:
    """Read the configs and return the available ai models

    Args:
        service_type (str): The using service type (g4f or Local)

    Returns:
        List: available ai models
    """    
    configs = read_configs()
    return [model['id'] for model in configs['models']['available'][service_type]['text']['casual']]


def make_db(name: str=None) -> str:
    """Create, config the database and execute some base queries on it

    Args:
        name (str, optional): the name of the created database. Defaults to None. if the name is None the name will read from the configs file

    Returns:
        string: the database name
    """    
    configs = read_configs()
    db_files_format = configs['format']['database']
    if name:
        if not name.endswith(db_files_format):
            name += db_files_format
        if not os.path.exists(name):
            with open(name, 'w') as file:
                file.close()
        db = DB(database_path=name)
        db.init()
        db.quit()
        return name
    else:
        return make_db(name=configs['defaults']['database_path'])


def store_settings(settings: dict) -> None:
    """Save the settings to the settings file by dump it using json moudel

    Args:
        settings (dict): a dict of settings
    """
    log("storing settings", 'debug')
    configs = read_configs()
    settings_file_name = configs['defaults']['settings_file_name']
    with open(settings_file_name, 'wt') as file:
        json.dump(settings, file)


def read_settings() -> dict:
    """
    Read the settings from the settings file by load it using json moudel
    if the file does not exist it will read the default settings from the configs file and write it in the settings file then returns the settings
    if a key of the settings missed it will replace it with the default value from the configs file

    Returns:
        dict: a dict of the settings
    """
    def check_dicts(dict1, dict2):
        for key in list(dict1.keys()):
            if key not in list(dict2.keys()):
                return True
            elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                if check_dicts(dict1[key], dict2[key]):
                    return True
    log("reading settings")
    configs = read_configs()
    settings_file_name = configs['defaults']['settings_file_name']
    default_settings = configs['settings']
    try:
        with open(settings_file_name, 'rt') as file:
            saved_settings = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log(f"Over Writing settings because there is an error FileNotFoundError or JSONDecodeError: {e}", "Error")
        store_settings(default_settings)
        return default_settings
    else:
        # Check if configs updated or a key missed
        over_write_dict = check_dicts(default_settings, saved_settings)
        if over_write_dict:
            log("Over Writing settings because changes detect.")
            store_settings(default_settings)
            return default_settings
        else:
            return saved_settings



def get_main_database_path() -> str:
    """get the main database path and create its tables

    Returns:
        string: the name of the database
    """
    database_path = get_main_database_path_()
    db = DB(database_path=database_path)
    db.init()
    db.quit()
    return database_path


def get_main_database_path_() -> str:
    """Detect the main database path

    Returns:
        str: the name of the database
    """
    configs = read_configs()
    database_path = configs['path']['database']
    databases = []
    files = os.listdir(database_path)
    db_files_format = configs['format']['database']
    for file in files:
        if file.endswith(db_files_format):
            databases.append(os.path.join(database_path, file))
    if len(databases) > 1:
        databases.sort()
        try:
            database__ = read_settings()['ai']['database_path']
            if database__.endswith(db_files_format) and os.path.exists(database__):
                return database__
        except:
            return databases[0]
        else:
            return databases[0]
    elif len(databases) == 1:
        return databases[0]
    elif not len(databases):
        return make_db()


def configure_app() -> None:
    """
    configure the app
    config include downloading the media (the pictures, json files which uses in the app), initalize the database
    """
    configs = read_configs()
    folders_to_create = configs['config']['create']['folders']
    for folder in folders_to_create:
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass
    settings_content = configs['defaults']['settings']
    settings_file = configs['config']['create']['files']['settings']
    with open(settings_file, 'wt') as file:
        file.write(json.dumps(settings_content))
        file.close()
    database_file = configs['config']['create']['files']['database']
    make_db(name=database_file)
    media_files_url = configs['urls']['media']
    for media_path in media_files_url.keys():
        media_path_ = os.path.join("storage/media", media_path)
        if os.path.exists(media_path_):
            continue
        url = media_files_url[media_path]['url']
        save_type = media_files_url[media_path]['save_type']
        content = get_file(url)
        with open(media_path_, save_type) as file:
            file.write(content)
    list_media()


def get_file(url: str) -> str | bytes:
    """Downloads the file and returns its content

    Args:
        url (str): the url of the file

    Returns:
        str | bytes: the files content
    """    
    return request__(method='get', url=url).content



class DB:
    """
    DB is a object for control the database
    """
    connection = None
    cursor = None
    db_path = None
    dictionary = False

    def __init__(self, database_path: str, dictionary: bool=True, check_same_thread: bool=False):
        self.db_path = database_path
        if not os.path.exists(database_path):
            log(f"Creating database in path: {database_path}")
        self.connection = sqlite3.connect(database_path, check_same_thread=check_same_thread)
        if dictionary:
            self.dictionary = True
            self.connection.row_factory = sqlite3.Row #https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
        log(f"Connected to database: {database_path}")
        self.cursor = self.connection.cursor()

    def commit(self) -> None:
        self.connection.commit()

    def quit(self) -> None:
        self.cursor.close()
        self.connection.close()
        log(f"database connection closed. path: {self.db_path}")

    def query(self, query: str, params: tuple=None, full_response=False, print_log=True) -> tuple | list | dict | None:
        if print_log:
            log(f"Running query: {query} -> params: {params}")
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.commit()
            if full_response:
                return self.cursor.fetchall() # return the result
            else:
                response = self.cursor.fetchall()
                return response
        except Exception as e:
            if print_log:
                log(f"Error in executing query: {query} -> {e}", 'Error')

    def to_dict(self, results, keys: list) -> dict | list[Any]:
        if self.dictionary: # if self.dictionary is True result is dict and we dont need to convert it to dict
            return results if results else []
        if results and len(results) >= 1 and (isinstance(results, list) or isinstance(results, tuple)) and isinstance(results[0], list) or isinstance(results[0], tuple):
            findall_results = []
            for result in results:
                dictionary = {}
                for i, key in enumerate(keys):
                    dictionary[key] = result[i]
                if not dictionary:
                    continue
                findall_results.append(dictionary)
            return findall_results
        else:
            result = results
            dictionary = {}
            for i, key in enumerate(keys):
                dictionary[key] = result[i]
            return dictionary


    def record_model(self, name: str, description: str="No description", version: str='Unknown') -> None | list[Any]:
        return self.query("INSERT INTO models (name, description, version) VALUES (?, ?, ?);", tuple([name, description, version]))

    def record_conversion(self, model_id: int, title: str) -> None | list[Any]:
        return self.query("INSERT INTO conversions (model_id, title) VALUES (?, ?);", tuple([model_id, title]))

    def update_conversion(self, conversion_id: int, title: str) -> None | list[Any]:
        return self.query("UPDATE conversions SET title = ? WHERE id = ?;", tuple([title, conversion_id]))

    def record_message(self, conversion_id: int, message: str, role: str) -> None | list[Any]:
        return self.query("INSERT INTO messages (conversion_id, message, role) VALUES (?, ?, ?);", tuple([conversion_id, message, role]))

    def record_server_model(self, name: str, url: str, description: str="No description", version: str='Unknown') -> None | list[Any]:
        return self.query("INSERT INTO server_models (name, description, version, url) VALUES (?, ?, ?, ?);", tuple([name, description, version, url]))

    def get_conversions(self) -> dict | list[dict] | None:
        return self.to_dict(self.query("SELECT id, model_id, title, created_at FROM conversions;"), ['id', 'model_id', 'title', 'created_at'])

    def get_models(self) -> dict | list[dict] | None:
        return self.to_dict(self.query("SELECT id, name, description, version, created_at FROM models;"), ['id', 'name', 'description', 'version', 'created_at', 'updated_at'])

    def get_model(self, model_id) -> dict | list[dict] | None:
        return self.to_dict(self.query("SELECT id, name, description, version, created_at FROM models WHERE id=?", tuple([model_id])), ['id', 'name', 'description', 'version', 'created_at', 'updated_at'])

    def get_conversion_messages(self, conversion_id: int) -> dict | list[dict] | None:
        return self.to_dict(self.query("SELECT id, conversion_id, message, role, send_time FROM messages WHERE conversion_id=? ORDER BY id ASC;", tuple([conversion_id])), ['id', 'conversion_id', 'message', 'role', 'send_time'])

    def get_conversion(self, conversion_id: int) -> dict | list[dict] | None:
        return self.to_dict(self.query(f"SELECT id, model_id, title, created_at FROM conversions WHERE id=?", tuple([conversion_id])), ['id', 'model_id', 'title', 'created_at'])

    def build_tables(self) -> None: # building the database tables
        sql_queries = [ # Some queries to build the tables
        """
        CREATE TABLE IF NOT EXISTS "models" (
            "id" INTEGER NOT NULL,
            "name" VARCHAR(255) NOT NULL UNIQUE,
            "description" TEXT DEFAULT "No description",
            "version" VARCHAR(50) DEFAULT NULL,
            "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "conversions" (
            "id"	INTEGER NOT NULL UNIQUE,
            "model_id"	INT NOT NULL,
            "title"	TEXT NOT NULL,
            "created_at"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "messages" (
            "id"	INTEGER NOT NULL UNIQUE,
            "conversion_id"	INT NOT NULL,
            "message"	TEXT NOT NULL,
            "role" VARCHAR(255) NOT NULL,
            "send_time"	TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS "server_models" (
            "id" INTEGER NOT NULL UNIQUE,
            "url" TEXT NOT NULL,
            "name" VARCHAR(255) NOT NULL,
            "description" TEXT DEFAULT "No description",
            "version" VARCHAR(50) DEFAULT NULL,
            "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
        ]
        for query in sql_queries:
            self.query(query, print_log=False) # run each query
    def init(self):
        if self.db_path in built_databases:
            return # skip running queries on databases which already build
        """
        initializing database, creating tables and insert default values(contains g4f models and their details)
        """
        self.build_tables()
        sql_queries = []
        all_models = read_configs()['models']['all']
        for model in all_models:
            model_name = model['id']
            description = f"Owned by {model['owned_by']}"
            sql_queries.append({'query': "INSERT OR IGNORE INTO models (name, description, version) VALUES (?, ?, ?);", 'params': (model_name, description, 'Unknown')})
        for query_info in sql_queries:
            self.query(query=query_info['query'], params=query_info['params'], print_log=False)
        built_databases.append(self.db_path)


def get_models_in_database() -> dict | list | tuple | None:
    db = DB(database_path=get_main_database_path())
    db.init()
    all_models = db.get_models()
    db.quit()
    return all_models


class AiClient:
    """Its a class for interacting with AI models"""
    service = ""
    service_type = ""
    conversion = []
    g4f_client = None
    base_url = None
    local_api_status = False # False means isn't running and True means it`s running.

    def init(self, api_key: str=None, ignore_database: bool=False, conversion_id: int | str=None, database_path: str=None, model: str=None, base_url: str=None, service_type: str='g4f', conversion: list=[], model_id: int=None, username='user'):
        log(f"Using {self.service} service")
        self.username: str = username
        self.api_key: str | None = api_key
        self.database_path: str = database_path
        self.conversion_id: int = conversion_id
        self.model: str = model
        self.conversion = conversion
        self.service_type: str = service_type
        self.base_url: str = base_url
        self.configs: dict = read_configs()
        self.ignore_database: bool = ignore_database
        self.model_id: int = model_id
        conversion_info = None
        if not self.ignore_database:
            if not self.database_path:
                self.database_path = get_main_database_path()
            self.database = DB(self.database_path)
            if self.conversion_id:
                conversion_info = self.database.get_conversion(self.conversion_id)[0]
            if not self.base_url:
                if not self.model_id and conversion_info:
                    self.model_id = int(conversion_info['model_id'])
                if not self.model and self.model_id:
                    self.model = self.database.get_model(self.model_id)[0]['name']
                if not self.model and self.service_type == 'g4f':
                    self.model = 'gpt-4o-mini'
        self.client = G4fClient()
        log(f"Successfully init.")

    def __init__(self):
        self.models = get_models_in_database()
        self.client = None
        self.model = None
        self.model_id = None
        self.database = None
        self.configs = None
        self.conversion_id = None
        self.database_path = None
        self.username = None
        self.api_key = None
        self.original_stdout = sys.stdout
        log("AiClient object created.")

    def record_messages_in_db(self, message: str, role: str) -> None:
        if not self.ignore_database:
            return self.database.record_message(message=message, conversion_id=self.conversion_id, role=role)

    def run_local_api_server_(self) -> None:
        """
        This function runs the local API server for the G4F service.
        """
        log_file_name = 'local_api_status.txt'
        try:
            try:
                os.remove(log_file_name)
            except:
                pass
            with open(log_file_name, 'wt') as f:
                f.write("Start Running API Server on localhost...")
                sys.stdout = f
                self.local_api_status = True
                run_api() # docs: https://g4f.mintlify.app/docs/core/usage/inference
        except KeyboardInterrupt:
            with open(log_file_name, 'at') as log_file:
                log_file.write(f"Stopped running API Server on localhost...")
        except Exception as error:
            sys.stdout = self.original_stdout
            log(f"An error: {error}", "error")
        finally:
            sys.stdout = self.original_stdout

    def run_local_api_server(self) -> None:
        """
        this function calls the run_local_api_server_ function in a separate thread.
        """
        self.local_api_thread = Thread(target=self.run_local_api_server_)
        self.local_api_thread.start()

    def ask(self, prompt: str):
        """sends a prompt to the AI model and returns its response

        Returns:
            str: the response if the AI model
        """        
        if self.service_type == 'g4f': # using g4f api server
            response = self.ask_g4f(prompt)
        elif self.service_type == 'local' and self.base_url:
            response = self.request_to_local(prompt) # using g4f api on localhost, api server on local will run by run_local_api_server function
        else:
            response = self.request_to_api(prompt)
        if not response[0]: # response is a tuple of (is_success, response)
            return response
        self.record_messages_in_db(prompt, role=self.username)
        log(f"Message from {self.username} recorded.", 'debug')
        self.record_messages_in_db(response[1], role=self.model)
        log(f"Message from {self.model} recorded.", 'debug')
        return response

    def request_to_local(self, prompt: str) -> list[bool, str]:
        """sends a prompt to the AI model on localhost and returns its response
        
        Args:
            prompt (str): the prompt to send to the AI model

        Returns:
            list[bool, str]: a list of (success: bool, message: str)
        """
        if self.local_api_status:
            return self.request_to_api(prompt)
        else:
            return [False, 'Local api server is off.']

    def request_to_api(self, prompt: str) -> list[bool, str]:
        """Sends a request to the AI model on web address and returns its response

        Args:
            prompt (str): the prompt to send to the AI model

        Returns:
            list[bool, str]: a list of (success: bool, message: str)
        """
        if not self.base_url.endswith("/v1/chat/completions"):
            self.base_url += "/v1/chat/completions"
        conversion_update = self.conversion
        conversion_update.append({"role": "user", "content": prompt})
        body = {
            "model": self.model,
            "stream": False,
            "messages": conversion_update
        }
        if self.api_key:
            body['api_key'] = self.api_key
        try:
            try:
                response = self.send(url=self.base_url, method='post', json=body)
                if response.status_code != 200:
                    response = f'status code {response.status_code} in sending request to server!\n'
                    if self.configs and 'status_codes' in self.configs and str(response.status_code) in self.configs['status_codes']:
                        response += self.configs['status_codes'][str(response.status_code)]
                    return [False, response]
                else:
                    json_response = response.json().get('choices', [])
                    response = json_response[0].get('message', {}).get('content', '')
            except Exception as e:
                raise e
            else:
                self.conversion.append({"role": "user", "content": prompt})
                self.conversion.append({'role': 'system', 'content': response})
        except Exception as e:
            return [False, f'Error: {e}']
        else:
            return [True, response]

    def ask_g4f(self, prompt: str) -> list[bool, str]:
        """Sends a request to the AI model using G4F service and returns its response

        Args:
            prompt (str): the prompt to send to the AI model

        Returns:
            list[bool, str]: a list of (success: bool, message: str)
        """
        try:
            conversion_update = self.conversion
            conversion_update.append({"role": "user", "content": prompt})
            try:
                if self.api_key:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=conversion_update,
                        api_key=self.api_key,
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=conversion_update,
                    )
                response = response.choices[0].message.content
            except Exception as e:
                raise e
            else:
                self.conversion.append({"role": "user", "content": prompt})
                self.conversion.append({'role': 'system', 'content': response})
        except Exception as e:
            return [False, f'Error: {e}']
        else:
            return [True, response]

    def send(self, method: str, url: str, json=None) -> str:
        """Sends a request to the specified URL using the specified method"""
        method = method.lower()
        try:
            response = request__(method, url, json=json)
            status = response.status_code
            if status != 200:
                log(f"Response {status} in sending request to {url} using method={method}", log_type='warn')
            else:
                log(f"Successfully request to {url} using method={method}")
            return response
        except Exception as e:
            log(f"Error in sending request to {url} using method={method} -> {e}")
            raise e


def list_media() -> list[str, str, str]:
    """makes a list of media (the pictures, json files which uses in the app)
    Downloads the media if it's not downloaded yet or it was removed

    Returns:
        list[str, str, ...]: list of media
    """
    configs = read_configs()
    media_files = configs['media']
    media_keys = list(media_files.keys())
    all_media = []
    for media_key in media_keys:
        all_media.extend(list(media_files[media_key].values()))
    all_media = set(all_media) # convert all_media list to a set to delete duplicated items
    for media in all_media:
        if os.path.isfile(media):
            continue
        try:
            shutil.rmtree(media) # maybe instead of file a directory with same name created, so first delete it
        except FileNotFoundError:
            pass
        real_file_name = media.split("/")[-1]
        url = get_file_url(real_file_name)
        with open(media, 'wb') as file:
            file.write(get_file(url))
            file.close()
    return media_files


def download_file(file_url: str, file_save_path: str, log_func: callable, progress_func: callable):
    """Downloads a file from the specified URL and saves it to the specified path, also logs the progress and the result

    Args:
        file_url (str): the url of the file to download
        file_save_path (str): the path to save file
        log_func (callable): a function to log the process
        progress_func (callable): a function to show and complete the progress bar
    """
    try:
        log_func(f"Downloading {file_url}...\n")
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        with open(file_save_path, 'wb') as f:
            downloaded_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
                progress_func(downloaded_size, total_size)

        log_func(f"Downloaded {file_url} to {file_save_path}\n")
    except Exception as e:
        log_func(f"Failed to download {file_url}: {e}\n")


def get_model_info(database: DB, **kwargs):
    """Fetch the info of a AI model from the informations in database"""
    key = list(kwargs.keys())[0]
    value = kwargs[key]
    all_models = database.get_models()
    for model in all_models:
        if model[key] == value:
            return model


if __name__ == '__main__':
    log("It isn't recommended.", log_type='Warn')
    # testing
    configure_app()

else:
    log("Core imported.")
    configure_app()

