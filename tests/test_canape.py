import os
import subprocess
from pathlib import Path

import numpy as np
import psutil
import pytest
from can.interfaces.vector import VectorBus, xldefine

import pycanape


def find_vector_examples() -> Path:
    vector_dir = Path(os.getenv("COMMONDOCUMENTS")) / "Vector"
    if not vector_dir.is_dir():
        raise FileNotFoundError

    example_dirs = sorted(vector_dir.glob("CANape Examples *"))
    if not example_dirs:
        raise FileNotFoundError

    return example_dirs[-1]


CANAPE_INSTALLED = bool(pycanape.utils.get_canape_versions())
XCPSIM_FOUND = False


if CANAPE_INSTALLED:
    EXAMPLES_DIR = find_vector_examples()
    XCPSIM_PATH = EXAMPLES_DIR / "_Simulators" / "XCPSim" / "xcpsim.exe"
    CANAPE_PROJECT = EXAMPLES_DIR / "XCPDemo"
    XCPSIM_FOUND = XCPSIM_PATH.exists() and CANAPE_PROJECT.exists()


@pytest.fixture(scope="session", autouse=True)
def set_channels():
    VectorBus.set_application_config(
        app_name="XCPsim",
        app_channel=0,
        hw_type=xldefine.XL_HardwareType.XL_HWTYPE_VIRTUAL,
        hw_index=0,
        hw_channel=0,
        bus_type=xldefine.XL_BusTypes.XL_BUS_TYPE_CAN,
    )
    VectorBus.set_application_config(
        app_name="CANape",
        app_channel=0,
        hw_type=xldefine.XL_HardwareType.XL_HWTYPE_VIRTUAL,
        hw_index=0,
        hw_channel=0,
        bus_type=xldefine.XL_BusTypes.XL_BUS_TYPE_CAN,
    )


@pytest.fixture()
def empty_canape():
    # initialization

    # search for open xcpsim processes and kill them
    for proc in psutil.process_iter():
        try:
            proc_name = proc.name()
        except psutil.AccessDenied:
            pass
        else:
            if proc_name.lower() == "xcpsim.exe":
                proc.kill()

    # start new XCPsim ECU simulator
    sim_process = subprocess.Popen(XCPSIM_PATH)

    # open new canape instance
    canape = pycanape.CANape(
        project_path=CANAPE_PROJECT,
        fifo_size=128,
        sample_size=256,
        time_out=0,
        clear_device_list=True,
        modal_mode=False,
    )
    # end of initialization

    yield canape

    # tear down
    canape.exit(close_canape=True)
    sim_process.kill()


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_create_module(empty_canape):
    canape = empty_canape

    assert canape.get_module_count() == 0

    created_module = canape.create_module(
        module_name="XCPsim",
        database_filename=os.path.join(CANAPE_PROJECT, "XCPsim.a2l"),
        driver=pycanape.DriverType.ASAP3_DRIVER_XCP,
        channel=pycanape.Channels.DEV_CAN1,
        go_online=True,
        enable_cache=-1,
    )
    assert canape.get_module_count() == 1
    assert isinstance(created_module, pycanape.Module)


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_remove_module(empty_canape):
    canape = empty_canape
    assert canape.get_module_count() == 0

    canape.create_module(
        module_name="XCPsim",
        database_filename=os.path.join(CANAPE_PROJECT, "XCPsim.a2l"),
        driver=pycanape.DriverType.ASAP3_DRIVER_XCP,
        channel=pycanape.Channels.DEV_CAN1,
        go_online=True,
        enable_cache=-1,
    )
    assert canape.get_module_count() == 1

    for idx in range(canape.get_module_count()):
        module = canape.get_module_by_index(idx)
        module.module_activation(activate=False)
        module.release_module()

    with pytest.raises(pycanape.CANapeError):
        canape.get_module_by_index(0)


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_get_module(empty_canape):
    canape = empty_canape

    created_module = canape.create_module(
        module_name="XCPsim",
        database_filename=os.path.join(CANAPE_PROJECT, "XCPsim.a2l"),
        driver=pycanape.DriverType.ASAP3_DRIVER_XCP,
        channel=pycanape.Channels.DEV_CAN1,
        go_online=True,
        enable_cache=-1,
    )

    module = canape.get_module_by_name("XCPsim")
    assert isinstance(module, pycanape.Module)
    assert module.module_handle == created_module.module_handle

    module = canape.get_module_by_index(created_module.module_handle.value)
    assert isinstance(module, pycanape.Module)
    assert module.module_handle == created_module.module_handle

    with pytest.raises(pycanape.CANapeError):
        _ = canape.get_module_by_name("NonExistingModule")


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_module_methods(empty_canape):
    canape = empty_canape
    module = canape.create_module(
        module_name="XCPsim",
        database_filename=os.path.join(CANAPE_PROJECT, "XCPsim.a2l"),
        driver=pycanape.DriverType.ASAP3_DRIVER_XCP,
        channel=pycanape.Channels.DEV_CAN1,
        go_online=True,
        enable_cache=-1,
    )
    database_path = module.get_database_path()
    assert Path(database_path).exists()
    assert Path(database_path).name == "XCPsim.a2l"

    database_info = module.get_database_info()
    assert database_info.file_name == "XCPsim.a2l"
    assert Path(database_info.file_path) == Path(database_path).parent
    assert database_info.file_type is pycanape.cnp_api.cnp_constants.DBFileType.ASAP2

    database_objects = module.get_database_objects()
    assert len(database_objects) > 1000

    assert module.is_module_active()
    module.module_activation(False)
    assert not module.is_module_active()
    module.module_activation(True)
    assert module.is_module_active()

    assert module.is_ecu_online()
    module.switch_ecu_on_offline(False)
    assert not module.is_ecu_online()
    module.switch_ecu_on_offline(True)
    assert module.is_ecu_online()

    assert module.get_communication_type() == "XCP"
    ecu_tasks = module.get_ecu_tasks()
    assert isinstance(ecu_tasks, dict)
    assert len(ecu_tasks) == 7
    assert all(isinstance(x, pycanape.EcuTask) for x in ecu_tasks.values())

    assert module.get_network_name() == "CAN_Network"
    assert module.has_resume_mode()

    module.reset_data_acquisition_channels_by_module()
    assert module.get_measurement_list_entries() == {}

    script = module.execute_script_ex(script_file=False, script='printf("Hello");')
    assert isinstance(script, pycanape.Script)

    module.release_module()


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_get_calibration_object(empty_canape):
    canape = empty_canape
    module = canape.create_module(
        module_name="XCPsim",
        database_filename=os.path.join(CANAPE_PROJECT, "XCPsim.a2l"),
        driver=pycanape.DriverType.ASAP3_DRIVER_XCP,
        channel=pycanape.Channels.DEV_CAN1,
        go_online=True,
        enable_cache=-1,
    )

    measurement_obj = module.get_calibration_object("KL1Output")
    assert isinstance(measurement_obj, pycanape.ScalarCalibrationObject)
    assert measurement_obj.name == "KL1Output"
    assert measurement_obj.object_type is pycanape.ObjectType.OTT_MEASURE
    assert measurement_obj.value == 1.0
    assert measurement_obj.min == 0.0
    assert measurement_obj.max == 255.0
    assert measurement_obj.min_ex == 0.0
    assert measurement_obj.max_ex == 255.0
    assert measurement_obj.precision == 3
    assert measurement_obj.unit == ""

    scalar_calib_obj = module.get_calibration_object("noise_ampl")
    assert isinstance(scalar_calib_obj, pycanape.ScalarCalibrationObject)
    assert scalar_calib_obj.name == "noise_ampl"
    assert scalar_calib_obj.object_type is pycanape.ObjectType.OTT_CALIBRATE
    assert scalar_calib_obj.value_type is pycanape.ValueType.VALUE
    assert scalar_calib_obj.value == 0.0

    curve_calib_obj = module.get_calibration_object("curve_kl2")
    assert isinstance(curve_calib_obj, pycanape.CurveCalibrationObject)
    assert curve_calib_obj.name == "curve_kl2"
    assert curve_calib_obj.object_type is pycanape.ObjectType.OTT_CALIBRATE
    assert curve_calib_obj.value_type is pycanape.ValueType.CURVE
    assert curve_calib_obj.dimension == 8
    assert np.array_equal(
        curve_calib_obj.axis,
        [0, 1, 2, 3, 4, 5, 6, 7],
    )
    assert np.array_equal(
        curve_calib_obj.values,
        [11, 22, 33, 44, 55, 66, 77, 88],
    )

    map_calib_obj = module.get_calibration_object("KF1")
    assert isinstance(map_calib_obj, pycanape.MapCalibrationObject)
    assert map_calib_obj.name == "KF1"
    assert map_calib_obj.object_type is pycanape.ObjectType.OTT_CALIBRATE
    assert map_calib_obj.value_type is pycanape.ValueType.MAP
    assert map_calib_obj.x_dimension == 8
    assert map_calib_obj.y_dimension == 8
    assert np.array_equal(map_calib_obj.x_axis, [0, 1, 2, 3, 4, 5, 6, 7])
    assert np.array_equal(map_calib_obj.y_axis, [0, 1, 2, 3, 4, 5, 6, 7])
    assert np.array_equal(
        map_calib_obj.values,
        [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.02],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.02, 0.03],
            [0.0, 0.0, 0.0, 0.0, 0.01, 0.01, 0.02, 0.03],
            [0.0, 0.0, 0.0, 0.01, 0.01, 0.02, 0.03, 0.04],
            [0.0, 0.01, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07],
            [0.01, 0.01, 0.01, 0.02, 0.04, 0.06, 0.08, 0.09],
            [0.01, 0.01, 0.02, 0.04, 0.05, 0.08, 0.09, 0.1],
            [0.01, 0.01, 0.03, 0.05, 0.08, 0.09, 0.1, 0.1],
        ],
    )

    axis_calib_obj = module.get_calibration_object("Curve1")
    assert isinstance(axis_calib_obj, pycanape.AxisCalibrationObject)
    assert axis_calib_obj.name == "Curve1"
    assert axis_calib_obj.object_type is pycanape.ObjectType.OTT_CALIBRATE
    assert axis_calib_obj.value_type is pycanape.ValueType.AXIS
    assert axis_calib_obj.dimension == 8
    assert np.array_equal(
        axis_calib_obj.axis,
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 12.0],
    )

    ascii_calib_obj = module.get_calibration_object("testString")
    assert isinstance(ascii_calib_obj, pycanape.AsciiCalibrationObject)
    assert ascii_calib_obj.name == "testString"
    assert ascii_calib_obj.object_type is pycanape.ObjectType.OTT_CALIBRATE
    assert ascii_calib_obj.value_type is pycanape.ValueType.ASCII
    assert ascii_calib_obj.len == 10
    assert ascii_calib_obj.ascii == "TestString"

    valblk_calib_obj = module.get_calibration_object("KL1")
    assert isinstance(valblk_calib_obj, pycanape.ValueBlockCalibrationObject)
    assert valblk_calib_obj.name == "KL1"
    assert valblk_calib_obj.object_type is pycanape.ObjectType.OTT_CALIBRATE
    assert valblk_calib_obj.value_type is pycanape.ValueType.VAL_BLK
    assert valblk_calib_obj.x_dimension == 16
    assert valblk_calib_obj.y_dimension == 1
    assert np.array_equal(
        valblk_calib_obj.values,
        [1, 2, 3, 4, 5, 6, 8, 12, 14, 11, 9, 7, 6, 5, 4, 3],
    )
