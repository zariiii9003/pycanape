# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT

import ctypes
import logging
import sys
import winreg
from collections.abc import Callable
from ctypes.util import find_library
from threading import Lock
from typing import Any, TypeVar

import psutil

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


LOG = logging.getLogger(__name__)
LOCK = Lock()

P1 = ParamSpec("P1")
T1 = TypeVar("T1")


def _synchronization_wrapper(
    func: Callable[P1, T1], func_name: str
) -> Callable[P1, T1]:
    """Use locks to assure thread safety.

    Without synchronization it is possible that Asap3GetLastError
    retrieves the error of the wrong function."""

    if func_name in ("Asap3GetLastError", "Asap3ErrorText"):
        return func

    def wrapper(*args, **kwargs):
        with LOCK:
            return func(*args, **kwargs)

    return wrapper


class CLibrary(ctypes.WinDLL):
    """Based on https://github.com/hardbyte/python-can/blob/develop/can/ctypesutil.py"""

    def __init__(self, library_or_path: str) -> None:
        library_path = find_library(library_or_path)
        if library_path is None:
            log_msg = "CANape API not found. Add CANape API location to environment variable `PATH`."
            LOG.warning(log_msg)
            raise FileNotFoundError(log_msg)

        super().__init__(library_path)

    @property
    def function_type(self):
        return ctypes.WINFUNCTYPE

    def map_symbol(self, func_name: str, restype=None, argtypes=(), errcheck=None) -> Callable[..., Any]:  # type: ignore[no-untyped-def]
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
            err_msg = f"Could not map function '{func_name}' from library {self._name}"
            raise ImportError(err_msg) from None

        symbol.__name__ = func_name  # type: ignore[attr-defined]

        if errcheck:
            symbol.errcheck = errcheck

        func = _synchronization_wrapper(symbol, func_name)

        setattr(self, func_name, func)
        return func


class CANapeError(Exception):
    def __init__(self, error_code: int, error_string: str, function: str) -> None:
        #: The error code according to :class:`~pycanape.cnp_api.cnp_constants.ErrorCodes`
        self.error_code = error_code
        super().__init__(f"{function} failed ({error_string})")

        # keep reference to args for pickling
        self._args = error_code, error_string, function

    def __reduce__(self):
        return CANapeError, self._args, {}


def _kill_canape_processes() -> None:
    # search for open CANape processes and kill them
    for proc in psutil.process_iter():
        try:
            proc_name = proc.name()
        except psutil.AccessDenied:
            pass
        else:
            if proc_name.lower() in ("canape.exe", "canape64.exe"):
                proc.kill()


def get_canape_path() -> str:
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\VECTOR\\CANape") as key:
        return winreg.QueryValueEx(key, "Path")[0]


def get_canape_datapath() -> str:
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\VECTOR\\CANape") as key:
        return winreg.QueryValueEx(key, "DataPath")[0]
