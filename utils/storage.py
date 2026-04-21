import json
import os
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CACHE_PATH = os.path.join(DATA_DIR, 'last_results.json')

os.makedirs(DATA_DIR, exist_ok=True)


def load_cached_results() -> List[Dict[str, Any]]:
    if not os.path.exists(CACHE_PATH):
        return []
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_cached_results(results: List[Dict[str, Any]]) -> None:
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def clear_cached_results() -> None:
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
