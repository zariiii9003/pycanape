import sys

# compatibility fix for python 3.7
if sys.version_info >= (3, 8):
    import importlib.metadata as importlib_metadata
else:
    import importlib_metadata

__version__ = importlib_metadata.metadata("pycanape")["Version"]

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
