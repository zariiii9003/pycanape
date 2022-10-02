__version__ = "0.5.0.dev0"

from typing import Dict, Any

RC: Dict[str, Any] = {"ENCODING": "latin-1"}  # runtime config

from .utils import CANapeError
from .cnp_api.cnp_constants import (
    Channels,
    DriverType,
    EventCode,
    MeasurementState,
    ObjectType,
    RecorderType,
    RecorderState,
    ValueType,
)
from .module import DBFileInfo, EcuTask, MeasurementListEntry, Module
from .daq_handling import FifoReader
from .recorder import Recorder
from .calibration_object import (
    ScalarCalibrationObject,
    AxisCalibrationObject,
    CurveCalibrationObject,
    MapCalibrationObject,
    AsciiCalibrationObject,
    ValueBlockCalibrationObject,
)
from .canape import CANape, AppVersion
