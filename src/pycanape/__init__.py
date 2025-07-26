# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT

__all__ = [
    "RC",
    "AppVersion",
    "AsciiCalibrationObject",
    "AxisCalibrationObject",
    "CANape",
    "CANapeDll",
    "CANapeError",
    "CANapeVersion",
    "Channels",
    "CurveCalibrationObject",
    "DatabaseInfo",
    "DllVersion",
    "DriverType",
    "EcuTask",
    "EventCode",
    "FifoReader",
    "MapCalibrationObject",
    "MeasurementListEntry",
    "MeasurementState",
    "Module",
    "ObjectType",
    "Recorder",
    "RecorderState",
    "RecorderType",
    "ScalarCalibrationObject",
    "Script",
    "ValueBlockCalibrationObject",
    "ValueType",
    "__version__",
    "calibration_object",
    "canape",
    "cnp_api",
    "config",
    "daq",
    "ecu_task",
    "get_canape_data_path",
    "get_canape_dll_path",
    "get_canape_path",
    "get_canape_versions",
    "module",
    "recorder",
    "script",
    "utils",
]

import contextlib
from importlib.metadata import PackageNotFoundError, version

from . import (
    calibration_object,
    canape,
    cnp_api,
    config,
    daq,
    ecu_task,
    module,
    recorder,
    script,
    utils,
)
from .calibration_object import (
    AsciiCalibrationObject,
    AxisCalibrationObject,
    CurveCalibrationObject,
    MapCalibrationObject,
    ScalarCalibrationObject,
    ValueBlockCalibrationObject,
)
from .canape import AppVersion, CANape, DllVersion
from .cnp_api.cnp_constants import (
    Channels,
    DriverType,
    EventCode,
    MeasurementState,
    ObjectType,
    RecorderState,
    RecorderType,
    ValueType,
)
from .cnp_api.cnp_prototype import CANapeDll
from .config import RC
from .daq import FifoReader
from .ecu_task import EcuTask
from .module import DatabaseInfo, MeasurementListEntry, Module
from .recorder import Recorder
from .script import Script
from .utils import (
    CANapeError,
    CANapeVersion,
    get_canape_data_path,
    get_canape_dll_path,
    get_canape_path,
    get_canape_versions,
)

with contextlib.suppress(PackageNotFoundError):
    __version__ = version("pycanape")
