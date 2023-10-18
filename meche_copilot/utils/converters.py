from typing import List, Type
from pydantic import BaseModel
from pathlib import Path
import re

def pydantic_to_jsonl(items: List[BaseModel], fpath: Path) -> None:
    with fpath.open("w") as f:
        for item in items:
            f.write(item.json() + "\n")

def pydantic_from_jsonl(fpath: Path, pydantic_class: Type[BaseModel]) -> List[BaseModel]:
    with fpath.open("r") as f:
        return [pydantic_class.parse_raw(line) for line in f]

def title_to_filename(title):
    # Convert to lowercase and replace spaces with underscores
    sanitized = title.lower().replace(" ", "_")
    # Remove any characters that are not alphanumeric or underscore
    valid_filename = re.sub(r'[^a-z0-9_]', '', sanitized)
    return valid_filename

def filename_to_title(filename):
    # Replace underscores with spaces and convert to title case
    title = filename.replace("_", " ").title()
    return title