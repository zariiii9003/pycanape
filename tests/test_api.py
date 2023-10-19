import pycanape


def test_toplevel_attributes() -> None:
    assert hasattr(pycanape, "__version__")
    assert hasattr(pycanape, "cnp_api")
    assert hasattr(pycanape, "calibration_object")
    assert hasattr(pycanape, "canape")
    assert hasattr(pycanape, "config")
    assert hasattr(pycanape, "daq")
    assert hasattr(pycanape, "ecu_task")
    assert hasattr(pycanape, "get_canape_data_path")
    assert hasattr(pycanape, "get_canape_dll_path")
    assert hasattr(pycanape, "get_canape_path")
    assert hasattr(pycanape, "get_canape_versions")
    assert hasattr(pycanape, "module")
    assert hasattr(pycanape, "recorder")
    assert hasattr(pycanape, "script")
    assert hasattr(pycanape, "utils")
    assert hasattr(pycanape, "AsciiCalibrationObject")
    assert hasattr(pycanape, "AxisCalibrationObject")
    assert hasattr(pycanape, "CANapeDll")
    assert hasattr(pycanape, "CANapeVersion")
    assert hasattr(pycanape, "CurveCalibrationObject")
    assert hasattr(pycanape, "MapCalibrationObject")
    assert hasattr(pycanape, "ScalarCalibrationObject")
    assert hasattr(pycanape, "ValueBlockCalibrationObject")
    assert hasattr(pycanape, "AppVersion")
    assert hasattr(pycanape, "CANape")
    assert hasattr(pycanape, "Channels")
    assert hasattr(pycanape, "DriverType")
    assert hasattr(pycanape, "EventCode")
    assert hasattr(pycanape, "MeasurementState")
    assert hasattr(pycanape, "ObjectType")
    assert hasattr(pycanape, "RecorderState")
    assert hasattr(pycanape, "RecorderType")
    assert hasattr(pycanape, "ValueType")
    assert hasattr(pycanape, "RC")
    assert hasattr(pycanape, "FifoReader")
    assert hasattr(pycanape, "DatabaseInfo")
    assert hasattr(pycanape, "EcuTask")
    assert hasattr(pycanape, "MeasurementListEntry")
    assert hasattr(pycanape, "Module")
    assert hasattr(pycanape, "Recorder")
    assert hasattr(pycanape, "Script")
    assert hasattr(pycanape, "CANapeError")
