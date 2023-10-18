import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PROJECT_ROOT = os.environ["PROJECT_ROOT"]
PROJECT_ROOT = Path(os.path.abspath(PROJECT_ROOT))
if not PROJECT_ROOT.exists():
    raise FileNotFoundError(f"Envar validator failed: Could not find {PROJECT_ROOT}")

DATA_CACHE = os.environ["DATA_CACHE"]
DATA_CACHE = PROJECT_ROOT / DATA_CACHE
DATA_CACHE.mkdir(parents=True, exist_ok=True)