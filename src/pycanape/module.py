import ctypes
from typing import NamedTuple, Dict

from . import DriverType
from .ecu_task import EcuTask
from .calibration_object import get_calibration_object, CalibrationObject
from .cnp_api import cnp_class, cnp_prototype, cnp_constants


class MeasurementListEntry(NamedTuple):
    task_id: int
    rate: int
    save_flag: bool
    disabled: bool
    object_name: str


class Module:
    def __init__(
        self,
        asap3_handle: cnp_class.TAsap3Hdl,
        module_handle: cnp_class.TModulHdl,
    ):
        self.asap3_handle = asap3_handle
        self.module_handle = module_handle

    def is_module_active(self) -> bool:
        """Return the activation state of the module.

        :return:
            activation state
        """
        active = ctypes.c_bool()
        cnp_prototype.Asap3IsModuleActive(
            self.asap3_handle,
            self.module_handle,
            ctypes.byref(active),
        )
        return active.value

    def module_activation(self, activate: bool = True):
        """Switches the module activation state.

        :param activate:
            True -> activate Module
            False -> deactivate Module
        """
        cnp_prototype.Asap3ModuleActivation(
            self.asap3_handle,
            self.module_handle,
            activate,
        )

    def is_ecu_online(self) -> bool:
        """Asks CANape whether a ECU is online or offline"""
        ecu_state = cnp_class.enum_type()
        cnp_prototype.Asap3IsECUOnline(
            self.asap3_handle, self.module_handle, ctypes.byref(ecu_state)
        )
        if ecu_state.value == cnp_constants.TAsap3ECUState.TYPE_SWITCH_ONLINE:
            return True

        return False

    def switch_ecu_on_offline(self, online: bool, download: bool = True):
        """Switches an ECU from online to offline and vice versa.

        :param online:
            Switch ECU online if True, switch ECU offline if False
        :param download:
            if this parameter is set to true CANape will
            execute an download in case of online = True
        """
        ecu_state = (
            cnp_constants.TAsap3ECUState.TYPE_SWITCH_ONLINE
            if online
            else cnp_constants.TAsap3ECUState.TYPE_SWITCH_OFFLINE
        )
        cnp_prototype.Asap3ECUOnOffline(
            self.asap3_handle,
            self.module_handle,
            ecu_state,
            download,
        )

    def get_module_name(self) -> str:
        """Get name of module."""
        buffer = ctypes.c_char_p()
        ptr = ctypes.pointer(buffer)

        cnp_prototype.Asap3GetModuleName(
            self.asap3_handle,
            self.module_handle,
            ptr,
        )
        return buffer.value.decode("ascii")

    def get_communication_type(self) -> str:
        """Get current communication type (e.g. "CAN")."""
        buffer = ctypes.c_char_p()
        cnp_prototype.Asap3GetCommunicationType(
            self.asap3_handle,
            self.module_handle,
            ctypes.pointer(buffer),
        )
        return buffer.value.decode("ascii")

    def get_ecu_tasks(self) -> Dict[str, EcuTask]:
        """Get available data acquisition tasks.

        :return:
            A dictionary with the ecu task description as keys
            and the `EcuTask` instances as values
        """
        task_info_array = (cnp_class.TTaskInfo2 * 32)()
        ptr_task_no = ctypes.pointer(ctypes.c_ushort())
        cnp_prototype.Asap3GetEcuTasks2(
            self.asap3_handle,
            self.module_handle,
            task_info_array,
            ptr_task_no,
            32,
        )
        cnp_task_info_list = [*task_info_array][: ptr_task_no.contents.value]

        def get_task_instance(task_info: cnp_class.TTaskInfo2):
            task = EcuTask(
                asap3_handle=self.asap3_handle,
                module_handle=self.module_handle,
                task_info=task_info,
            )
            return task

        ecu_task_list = [get_task_instance(ti) for ti in cnp_task_info_list]
        return {et.description: et for et in ecu_task_list}

    def get_network_name(self) -> str:
        """Receives the name of the used network."""
        c_name = ctypes.create_string_buffer(256)
        cnp_prototype.Asap3GetNetworkName(
            self.asap3_handle,
            self.module_handle,
            ctypes.cast(ctypes.byref(c_name), ctypes.c_char_p),
            ctypes.byref(ctypes.c_uint()),
        )
        return c_name.value.decode("ascii")

    def get_ecu_driver_type(self) -> DriverType:
        """Retrieves the drivertype of an ECU.

        :return:
            DriverType enum
        """
        c_driver_type = cnp_class.enum_type()
        cnp_prototype.Asap3GetEcuDriverType(
            self.asap3_handle,
            self.module_handle,
            ctypes.byref(c_driver_type),
        )
        return DriverType(c_driver_type.value)

    def get_calibration_object(self, name: str) -> CalibrationObject:
        return get_calibration_object(self.asap3_handle, self.module_handle, name)

    def has_resume_mode(self) -> bool:
        """Information about the Resume mode.

        :return:
            Function returns True if the device supports resume mode.
        """
        bln = ctypes.c_bool()
        cnp_prototype.Asap3HasResumeMode(
            self.asap3_handle,
            self.module_handle,
            ctypes.byref(bln),
        )
        return bln.value

    def get_measurement_list_entries(self) -> Dict[str, MeasurementListEntry]:
        """Retrieve the entries from the CANape Measurement list.

        :return:
            A `dict` of Measurement list entries that uses the object name of
            the entries as key
        """
        entries = cnp_class.MeasurementListEntries()
        ptr = ctypes.pointer(ctypes.pointer(entries))
        cnp_prototype.Asap3GetMeasurementListEntries(
            self.asap3_handle,
            self.module_handle,
            ptr,
        )
        entries = ptr.contents[0]

        res = {}
        for idx in range(0, entries.ItemCount):
            c_entry = entries.Entries[idx][0]
            mle = MeasurementListEntry(
                task_id=c_entry.taskId,
                rate=c_entry.rate,
                save_flag=c_entry.SaveFlag,
                disabled=c_entry.Disabled,
                object_name=c_entry.ObjectName.decode("ascii"),
            )
            res[mle.object_name] = mle
        return res

    def reset_data_acquisition_channels_by_module(self):
        """Clears the data acquisition channel list of a specific module.

        .. note::
            this function only clears these measurement objects from the
            API-Measurement-List which are defined by API
        """
        cnp_prototype.Asap3ResetDataAcquisitionChnlsByModule(
            self.asap3_handle,
            self.module_handle,
        )

    def release_module(self):
        cnp_prototype.Asap3ReleaseModule(
            self.asap3_handle,
            self.module_handle,
        )