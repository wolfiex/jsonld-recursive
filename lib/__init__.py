"""
jsonld-recursive Python client library
"""

from .ldr_client import LdrClient
from .test_install import test, get_test_data_dir

try:
    from .version import __version__
except ImportError:
    __version__ = "unknown"
__all__ = ["LdrClient", "test", "get_test_data_dir"]
