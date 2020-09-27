import os
import subprocess

import pytest
import psutil
from can.interfaces.vector import VectorBus, xldefine

import pycanape


XCPSIM_PATH = os.path.join(
    pycanape.utils.get_canape_datapath(),
    "Examples",
    "_Simulators",
    "XCPSim",
    "xcpsim.exe",
)
CANAPE_PROJECT = os.path.join(
    pycanape.utils.get_canape_datapath(),
    "Examples",
    "XCPDemo",
)


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


class TestCanape:
    def test_create_module(self, empty_canape):
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

    def test_remove_module(self, empty_canape):
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

        for idx in range(0, canape.get_module_count()):
            module = canape.get_module_by_index(idx)
            module.release_module()

        assert canape.get_module_count() == 0

    def test_get_module(self, empty_canape):
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
            module = canape.get_module_by_name("NonExistingModule")
