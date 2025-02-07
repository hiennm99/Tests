"""" This module"""
import json
import os
import pickle


async def save_binary_file(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


async def load_binary_file(file_path):
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


async def load_json_file(file_path: str):
    """
    Load a JSON file as a dictionary.
    Creates an empty file if it doesn't exist.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Contents of the JSON file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding="UTF-8") as file:
            json.dump({}, file)

    with open(file_path, 'rb') as file:
        data = json.loads(file.read())
        data = {int(k): v for k, v in data.items()}
        return data


async def save_json_file(pools: dict, file_path: str):
    """
    Save a dictionary to a JSON file, overwriting if it exists.

    Args:
        pools (dict): Dictionary to save.
        file_path (str): Path to the JSON file.
    """
    with open(file_path, 'w', encoding="UTF-8") as file:
        file.write(json.dumps(pools, indent=4))
