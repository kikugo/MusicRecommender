import json, os, time
from typing import Any, Dict

CACHE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
RECS_FILE = os.path.join(CACHE_PATH, 'recommendations_cache.json')
TTL_SECONDS = 60*60*24  # 1 day

os.makedirs(CACHE_PATH, exist_ok=True)


def _load() -> Dict[str, Any]:
    if os.path.exists(RECS_FILE):
        try:
            with open(RECS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save(data: Dict[str, Any]):
    with open(RECS_FILE, 'w') as f:
        json.dump(data, f)

def get(key: str):
    data = _load()
    entry = data.get(key)
    if not entry:
        return None
    if time.time() - entry['ts'] > TTL_SECONDS:
        # stale
        data.pop(key, None)
        _save(data)
        return None
    return entry['value']


def set(key: str, value: Any):
    data = _load()
    data[key] = {'value': value, 'ts': time.time()}
    _save(data) 