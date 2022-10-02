# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import ctypes
import sys
from unittest.mock import MagicMock

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pyCANape"
copyright = "2022, Artur Drogunow"
author = "Artur Drogunow"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Include documentation from both the class level and __init__
autoclass_content = "both"

# mock Winodws specific modules and attributes for readthedocs.io (runs on ubuntu)
sys.modules["winreg"] = MagicMock()
ctypes.WinDLL = ctypes.CDLL
ctypes.WINFUNCTYPE = ctypes.CFUNCTYPE
ctypes.wintypes = MagicMock()
ctypes.wintypes.BYTE = ctypes.c_ubyte
ctypes.wintypes.BOOL = ctypes.c_bool
ctypes.wintypes.UINT = ctypes.c_uint
ctypes.wintypes.DWORD = ctypes.c_longlong
ctypes.wintypes.MAX_PATH = 255


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
