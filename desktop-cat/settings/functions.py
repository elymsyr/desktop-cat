from json import load, dump
from os.path import exists
from json.decoder import JSONDecodeError
from threading import Thread, current_thread

CONFIG_PATH = "zconfig.json"
BACKUP_CONFIG = {
        "config": {
            "prefix": "*",
            "paths": {
                "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
                "gifs": "media\\gifs",
                "falling_gif": "media\\gifs_others\\falling.gif",
                "command_bg": "media\\messagebox.png",
                "tray_ico": "media\\tray-icon.png",
                "font": "media\\pixelmix.ttf",
                "books_bg": "media\\books",
                "config-json": "data\\config.json"
            },
            "fonts": {
                "current_font_name": "pixelmix",
                "default_font_size": 10
            }
        }
    }
BACKUP_WORKLOADS = {"workloads":{"workload_data": {},"workloads": {}}}
WORKLOADS_PATH = 'zworkloads.json'

BACKUPS:dict = {
    'config': {'path': CONFIG_PATH, 'backup':BACKUP_CONFIG},
    'workloads': {'path': WORKLOADS_PATH, 'backup':BACKUP_WORKLOADS}
} 

class CommandException(Exception):
    def __init__(self, 
                 *args,
                 string_to_book: str = None,
                 file_error: str = None,
                 workload_name: str = None
                 ):
        self.string_to_book:str = string_to_book
        self.args: tuple = args
        self.file_error: str = file_error
        self.workload_name: str = workload_name

def find_key(path: str):
    """
    Retrieve the value from the dictionary at the specified `path`.
    Returns None if the path does not exist.
    """
    keys = path.split('.')
    current = get_data(keys[0])
    try:
        for key in keys[:]:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return None
    
def update_key(path: str, value: str | int | list | dict) -> None:
    """
    Update the dictionary with the given `value` at the specified `path`.
    If the path doesn't exist, it will be created.
    """
    keys = path.split('.')
    new_dict = get_data(keys[0]).copy()
    current = new_dict
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    set_data(data=new_dict, file=keys[0])
    
    
def delete_key(path: str) -> None:
    """
    Delete a key from the dictionary at the specified `path`.
    """
    keys = path.split('.')
    new_dict = get_data(keys[0]).copy()
    current = new_dict
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    del current[keys[-1]]
    set_data(data=new_dict, file=keys[0])

def format_string(string: str, size: int=30) -> str:
    """Formats string to a better visualization.

    Args:
        string (str)
        size (int, optional): Defaults to 30.

    Returns:
        str: Formatted string.
    """
    if len(string) > size:
        formatted_string = string[:size]
    else:
        formatted_string = string.ljust(size)
    return formatted_string

def get_data(file: str = None) -> None | dict:
    """Get config.json data as dictionary. Returns None if file does not exists or not unspoilt.

    Returns:
        dict: Data
    """
    data: dict
    if exists(BACKUPS[file]['path']):
        try:
            with open(BACKUPS[file]['path'], 'r') as dict_data:
                data = load(dict_data)
            if has_all_keys(current_config=data, main_config=BACKUPS[file]['backup'], file=file):
                return data
        except Exception:
            return None

def set_data(data: dict, file:str='config') -> None:
    """Write data to config.json

    Args:
        data (dict): Data
    """
    with open(BACKUPS[file]['path'], 'w') as dict_data:
        dump(data, dict_data, indent=4)
        
def has_all_keys(current_config: dict, main_config: dict, file: str = 'config') -> bool:
    """
    Check if current config has all the keys of the main config fie, recursively.
    """
    if file == 'config': return (
        set(current_config) == set(main_config) and
        set(current_config['config']) == set(main_config['config']) and
        set(current_config['config']['paths']) == set(main_config['config']['paths']) and
        set(current_config['config']['fonts']) == set(main_config['config']['fonts'])
    )
    elif file == 'workloads': return set(current_config) == set(main_config)


def safe_get_data():
    data = get_data()
    if not data:
        with open(CONFIG_PATH, 'w+') as file:
            dump(BACKUP_CONFIG, file, indent=4)
    return get_data()

def reset_file(file: str):
    with open(BACKUPS[file]['path'], 'w+') as dict_data:
        dump(BACKUPS[file]['backup'], dict_data, indent=4)