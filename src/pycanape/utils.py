import ctypes
import winreg
from ctypes.util import find_library
import logging

LOG = logging.getLogger(__name__)


class CLibrary(ctypes.WinDLL):
    """Based on https://github.com/hardbyte/python-can/blob/develop/can/ctypesutil.py"""

    def __init__(self, library_or_path: str):
        super().__init__(find_library(library_or_path))

    @property
    def function_type(self):
        return ctypes.WINFUNCTYPE

    def map_symbol(self, func_name: str, restype=None, argtypes=(), errcheck=None):
        """
        Map and return a symbol (function) from a C library. A reference to the
        mapped symbol is also held in the instance
        :param str func_name:
            symbol_name
        :param ctypes.c_* restype:
            function result type (i.e. ctypes.c_ulong...), defaults to void
        :param tuple(ctypes.c_* ... ) argtypes:
            argument types, defaults to no args
        :param callable errcheck:
            optional error checking function, see ctypes docs for _FuncPtr
        """
        if argtypes:
            prototype = ctypes.WINFUNCTYPE(restype, *argtypes)
        else:
            prototype = ctypes.WINFUNCTYPE(restype)
        try:
            symbol = prototype((func_name, self))
        except AttributeError:
            raise ImportError(
                "Could not map function '{}' from library {}".format(
                    func_name, self._name
                )
            )

        setattr(symbol, "__name__", func_name)
        LOG.debug(
            f'Wrapped function "{func_name}", result type: {type(restype)}, error_check {errcheck}'
        )

        if errcheck:
            symbol.errcheck = errcheck

        setattr(self, func_name, symbol)
        return symbol


class CANapeError(Exception):
    def __init__(self, error_code, error_string, function):
        self.error_code = error_code
        super().__init__(f"{function} failed ({error_string})")

        # keep reference to args for pickling
        self._args = error_code, error_string, function

    def __reduce__(self):
        return CANapeError, self._args, {}


def get_canape_path() -> str:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\VECTOR\\CANape")
    return winreg.QueryValueEx(key, "Path")[0]


def get_canape_datapath() -> str:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\VECTOR\\CANape")
    return winreg.QueryValueEx(key, "DataPath")[0]
