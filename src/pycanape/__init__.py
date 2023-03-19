# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT

__version__ = "0.5.0"

from typing import Any, Dict

from .calibration_object import (
    AsciiCalibrationObject,
    AxisCalibrationObject,
    CurveCalibrationObject,
    MapCalibrationObject,
    ScalarCalibrationObject,
    ValueBlockCalibrationObject,
)
from .canape import AppVersion, CANape
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
from .daq import FifoReader
from .module import DBFileInfo, EcuTask, MeasurementListEntry, Module
from .recorder import Recorder
from .utils import CANapeError

RC: Dict[str, Any] = {"ENCODING": "latin-1"}  # runtime config
