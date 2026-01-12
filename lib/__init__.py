"""
jsonld-recursive Python client library
"""

from .ldr_client import LdrClient
from .test_install import test, get_test_data_dir

__version__ = "1.0.0"
__all__ = ["LdrClient", "test", "get_test_data_dir"]
