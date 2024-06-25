from json import load, dump
from os.path import exists
from json.decoder import JSONDecodeError

CONFIG_PATH = "zconfig.json"
BACKUP_CONFIG = 'zconfig_backup.json'

class CommandException(Exception):
    def __init__(self, 
                 *args,
                 string_to_book: str = None
                 ):
        self.string_to_book:str = string_to_book
        self.args: tuple = args
        
def check_config_file() -> bool:
    """Checks if configuration file exists and unspoilt.
    """
    if exists(CONFIG_PATH):
        if has_all_keys_recursive(current_config=get_data(CONFIG_PATH), main_config=get_data(BACKUP_CONFIG)):
            try: 
                get_data()
                return True
            except JSONDecodeError as json_decode_error: 
                return False
    return False

def find_key(path: str):
    """
    Retrieve the value from the dictionary at the specified `path`.
    Returns None if the path does not exist.
    """
    keys = path.split('.')
    current = get_data()
    try:
        for key in keys:
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
    new_dict = get_data().copy()
    current = new_dict
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    set_data(data=new_dict)
    
def delete_key(path: str) -> None:
    """
    Delete a key from the dictionary at the specified `path`.
    """
    keys = path.split('.')
    new_dict = get_data().copy()
    current = new_dict
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    del current[keys[-1]]
    set_data(data=new_dict)

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

def get_data(path:str=CONFIG_PATH) -> dict:
    """Get config.json data as dictionary

    Returns:
        dict: Data
    """
    with open(path, 'r') as file:
        return load(file)

def set_data(data: dict, path:str=CONFIG_PATH) -> None:
    """Write data to config.json

    Args:
        data (dict): Data
    """
    with open(path, 'w') as file:
        dump(data, file, indent=4)
        
def has_all_keys_recursive(current_config: dict, main_config: dict) -> bool:
    """
    Check if current config has all the keys of the main config fie, recursively.
    """
    return (
        set(current_config) == set(main_config) and
        set(current_config['config']) == set(main_config['config']) and
        set(current_config['config']['paths']) == set(main_config['config']['paths']) and
        set(current_config['config']['fonts']) == set(main_config['config']['fonts'])
    )        
