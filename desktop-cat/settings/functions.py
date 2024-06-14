import json
from functools import reduce
from threading import Thread, current_thread

def find_key(path: str):
    """
    Retrieve the value from dictionary `d` at the specified `path`.
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
    Update dictionary `d` with the given `value` at the specified `path`.
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

def get_data() -> dict:
    """Get config.json data as dictionary

    Returns:
        dict: Data
    """
    data: dict
    with open('zconfig.json', 'r') as file:
        data = json.load(file)
    return data

def set_data(data: dict) -> None:
    """Write data to config.json

    Args:
        data (dict): Data
    """
    with open('zconfig.json', 'w') as file:
        json.dump(data, file, indent=4)        
