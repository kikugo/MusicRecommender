from .cache import get, set  # re-export cache helpers
from .helpers import calculate_similarity, calculate_embedding_similarity

# Make submodules available as attributes (e.g., `from src.utils import cache`)
import importlib as _importlib
import sys as _sys

_cache_module = _importlib.import_module(__name__ + '.cache')
_sys.modules[__name__ + '.cache'] = _cache_module

# Also expose via attribute on parent package
cache = _cache_module 