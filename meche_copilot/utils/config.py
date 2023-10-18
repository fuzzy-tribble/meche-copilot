from json import load
import re
import os
from box import Box
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

def replace_dashes_with_underscores_in_keys(d):
    if isinstance(d, Box) or isinstance(d, dict):
        new_d = {k.replace('-', '_'): replace_dashes_with_underscores_in_keys(v) for k, v in d.items()}
        return Box(new_d) if isinstance(d, Box) else new_d
    elif isinstance(d, list):
        return [replace_dashes_with_underscores_in_keys(v) for v in d]
    else:
        return d

def find_config(config_fname: str = './session-config.yml') -> str:
    config_fname = Path(config_fname)
    if config_fname.name in os.listdir(config_fname.parent):
        return config_fname
    raise FileNotFoundError(f"Could not find {config_fname} in {config_fname.parent}")

def load_config(config_fpath: str, substitute=True) -> Box:
    with open(config_fpath, 'r') as config_file:
        config = Box.from_yaml(config_file, conversion_box=True)

    # Replace dashes with underscores in keys
    config = replace_dashes_with_underscores_in_keys(config)

    if substitute:
        load_dotenv(find_dotenv())
        config = replace_values(config)
    return config

def replace_values(config):
    for key, value in config.items():
        if isinstance(value, str):
            # Replace ${var} with the value from environment variable
            replaced_value = re.sub(r'\$\{(.+?)\}', lambda x: os.getenv(x.group(1)), value)

            if value != replaced_value:
                # print(f"Replaced {value} with {replaced_value}")
                config[key] = replaced_value
        elif isinstance(value, dict):
            # If the value is a dictionary, recursively apply the same process
            config[key] = replace_values(value)
    return config
