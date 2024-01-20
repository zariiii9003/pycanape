# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT
import contextlib
import logging
import platform
import re
import winreg
from ctypes.util import find_library
from enum import IntEnum
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

import psutil

LOG = logging.getLogger(__name__)


class CANapeVersion(IntEnum):
    CANAPE_17 = 17
    CANAPE_18 = 18
    CANAPE_19 = 19
    CANAPE_20 = 20
    CANAPE_21 = 21
    CANAPE_22 = 22
    CANAPE_23 = 23


class CANapeError(Exception):
    def __init__(self, error_code: int, error_string: str, function: str) -> None:
        #: The error code according to :class:`~pycanape.cnp_api.cnp_constants.ErrorCodes`
        self.error_code = error_code
        super().__init__(f"{function} failed ({error_string})")

        # keep reference to args for pickling
        self._args = error_code, error_string, function

    def __reduce__(self) -> Union[str, Tuple[Any, ...]]:
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


def get_canape_versions() -> List[CANapeVersion]:
    """Return a list of all CANape versions, that can be found in Windows Registry."""
    versions: List[CANapeVersion] = []
    with contextlib.suppress(FileNotFoundError), winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\VECTOR\\CANape"
    ) as key:
        _sub_key_count, value_count, _last_modified = winreg.QueryInfoKey(key)
        for idx in range(value_count):
            name, _data, _type = winreg.EnumValue(key, idx)
            if not re.match(r"Path\d{3}", name):
                continue
            try:
                version_number = re.sub(pattern=r"Path", repl="", string=name)
                versions.append(CANapeVersion(int(version_number[:2])))
            except ValueError:
                continue
    return versions


def get_canape_path(version: Optional[CANapeVersion] = None) -> Path:
    """Return the path to the CANape installation from Windows registry.

    :param version:
        Select the CANape version that shall be found. If ``None``,
        it will usually return the version, that was installed last.
    :return:
        Path to the CANape installation.
    """
    name = f"Path{version.value}0" if version else "Path"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\VECTOR\\CANape") as key:
        try:
            return Path(winreg.QueryValueEx(key, name)[0])
        except FileNotFoundError:
            err_msg = "CANape path not found in Windows registry."
            raise FileNotFoundError(err_msg) from None


def get_canape_data_path(version: Optional[CANapeVersion] = None) -> Path:
    """Return the path to the CANape data folder from Windows registry.

    :param version:
        Select the CANape version that shall be found. If ``None``,
        it will usually return the version, that was installed last.
    :return:
        Path to the CANape data folder.
    """
    name = f"DataPath{version.value}0" if version else "DataPath"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\VECTOR\\CANape") as key:
        try:
            return Path(winreg.QueryValueEx(key, name)[0])
        except FileNotFoundError:
            err_msg = "CANape data path not found in Windows registry."
            raise FileNotFoundError(err_msg) from None


def get_canape_dll_path(version: Optional[CANapeVersion] = None) -> Path:
    """Return the path to the CANapAPI.dll from Windows registry or PATH.

    :param version:
        Select the CANape version that shall be found. If ``None``,
        it will usually return the version, that was installed last.
    :return:
        Path to the CANapAPI.dll.
    """
    dll_name = "CANapAPI64" if platform.architecture()[0] == "64bit" else "CANapAPI"

    # try to find dll via registry entry
    with contextlib.suppress(FileNotFoundError):
        canape_path = get_canape_path(version)
        dll_path = canape_path / "CANapeAPI" / (dll_name + ".dll")
        if dll_path.exists():
            return dll_path

    # try to find dll via PATH environment variable
    if dll_path_string := find_library(dll_name):
        return Path(dll_path_string)

    err_msg = "CANape DLL not found."
    raise FileNotFoundError(err_msg)
