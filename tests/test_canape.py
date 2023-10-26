import os
import subprocess
from pathlib import Path
from typing import Callable, Iterator, List

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


@pytest.fixture()
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


def start_xcpsim() -> "subprocess.Popen[bytes]":
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
    return subprocess.Popen(XCPSIM_PATH)


def get_canape_instance(modal_mode: bool) -> pycanape.CANape:
    return pycanape.CANape(
        project_path=CANAPE_PROJECT,
        fifo_size=128,
        sample_size=256,
        time_out=0,
        clear_device_list=True,
        modal_mode=modal_mode,
    )


@pytest.fixture()
def canape_fixture() -> Iterator[Callable[[bool], pycanape.CANape]]:
    sim_process = start_xcpsim()

    # use the list to save a reference to the instance
    canape_instances: List[pycanape.CANape] = []

    def _callback(modal_mode: bool) -> pycanape.CANape:
        canape = get_canape_instance(modal_mode=modal_mode)
        canape_instances.append(canape)
        return canape

    try:
        yield _callback

    finally:
        for instance in canape_instances:
            instance.exit(close_canape=True)

        sim_process.kill()


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_canape(canape_fixture: Callable[[bool], pycanape.CANape], set_channels):
    canape = canape_fixture(True)

    assert canape.has_mcd3_license()

    app_version = canape.get_application_version()
    assert isinstance(app_version, pycanape.AppVersion)

    dll_version = canape.get_dll_version()
    assert isinstance(dll_version, pycanape.DllVersion)

    assert Path(canape.get_project_directory()) == CANAPE_PROJECT
    assert canape.get_module_count() == 1

    canape.set_interactive_mode(True)
    canape.set_interactive_mode(False)

    module = canape.get_module_by_name("XCPsim")
    module.module_activation(True)
    module.switch_ecu_on_offline(True)

    network_name = module.get_network_name()
    assert canape.is_network_activated(network_name)

    assert canape.get_recorder_count() == 2
    assert isinstance(canape.get_selected_recorder(), pycanape.Recorder)
    assert isinstance(canape.get_recorder_by_index(0), pycanape.Recorder)

    blf_recorder = canape.define_recorder(
        recorder_name="MyBlfRecorder",
        recorder_type=pycanape.RecorderType.eTRecorderTypeBLF,
    )
    assert canape.get_recorder_count() == 3
    assert isinstance(blf_recorder, pycanape.Recorder)
    assert blf_recorder.get_name() == "MyBlfRecorder"
    assert (
        blf_recorder.get_mdf_filename()
        == "{RECORDER}_{YEAR}-{MONTH}-{DAY}_{HOUR}-{MINUTE}-{SECOND}.blf"
    )

    assert Path(canape.get_cna_filename()) == CANAPE_PROJECT / "XCPsimDemo.cna"
    canape.load_cna_file(CANAPE_PROJECT / "XCPsimDemo.cna")

    assert (
        canape.get_measurement_state()
        is pycanape.MeasurementState.eT_MEASUREMENT_STOPPED
    )
    canape.start_data_acquisition()
    assert (
        canape.get_measurement_state()
        is pycanape.MeasurementState.eT_MEASUREMENT_THREAD_RUNNING
    )
    canape.stop_data_acquisition()
    assert (
        canape.get_measurement_state()
        is pycanape.MeasurementState.eT_MEASUREMENT_STOPPED
    )


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_create_module(canape_fixture: Callable[[bool], pycanape.CANape], set_channels):
    canape = canape_fixture(False)

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
def test_remove_module(canape_fixture: Callable[[bool], pycanape.CANape], set_channels):
    canape = canape_fixture(False)
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
def test_get_module(canape_fixture: Callable[[bool], pycanape.CANape], set_channels):
    canape = canape_fixture(False)
    canape.create_module(
        module_name="XCPsim",
        database_filename=os.path.join(CANAPE_PROJECT, "XCPsim.a2l"),
        driver=pycanape.DriverType.ASAP3_DRIVER_XCP,
        channel=pycanape.Channels.DEV_CAN1,
        go_online=True,
        enable_cache=-1,
    )

    module = canape.get_module_by_name("XCPsim")
    assert isinstance(module, pycanape.Module)
    assert module.module_handle == module.module_handle

    module = canape.get_module_by_index(module.module_handle.value)
    assert isinstance(module, pycanape.Module)
    assert module.module_handle == module.module_handle

    with pytest.raises(pycanape.CANapeError):
        _ = canape.get_module_by_name("NonExistingModule")


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_module_methods(
    canape_fixture: Callable[[bool], pycanape.CANape], set_channels
):
    canape = canape_fixture(False)
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

    assert module.get_ecu_driver_type() is pycanape.DriverType.ASAP3_DRIVER_XCP

    script = module.execute_script_ex(script_file=False, script='printf("Hello");')
    assert isinstance(script, pycanape.Script)

    module.release_module()


@pytest.mark.skipif(not XCPSIM_FOUND, reason="CANape example project not found")
def test_get_calibration_object(
    canape_fixture: Callable[[bool], pycanape.CANape], set_channels
):
    canape = canape_fixture(False)
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
