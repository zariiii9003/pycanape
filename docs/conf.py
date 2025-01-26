# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import ctypes
import os
from importlib.metadata import version as get_version
from unittest.mock import MagicMock

os.environ["SPHINX_BUILD"] = "1"

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pyCANape"
copyright = "2022, Artur Drogunow"
author = "Artur Drogunow"

# The full version, including alpha/beta/rc tags.
release: str = get_version("pycanape")
# The short X.Y version.
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

# tls_verify = False
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "packaging": ("https://packaging.pypa.io/en/stable/", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Include documentation from both the class level and __init__
autoclass_content = "both"

# location of typehints
autodoc_typehints = "both"

nitpick_ignore = [
    ("py:class", "pycanape.cnp_api.cnp_class.LP_tAsap3Hdl"),
    ("py:class", "pycanape.cnp_api.cnp_class.LP_c_ulong"),
    ("py:class", "npt.NDArray"),
    ("py:class", "npt.DTypeLike"),
    ("py:class", "np.float64"),
    ("py:class", "numpy.float64"),
    ("py:class", "numpy.typing._dtype_like._SupportsDType"),
    ("py:class", "numpy.typing._dtype_like._DTypeDict"),
    ("py:class", "ctypes.wintypes.LP_c_ulong"),
    ("py:class", "ctypes.POINTER"),
]

# mock Winodws specific modules and attributes for readthedocs.io (runs on ubuntu)
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
