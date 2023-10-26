# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT
import copy
import ctypes
import fnmatch
import os.path
from typing import Dict, List, NamedTuple, Optional

from .calibration_object import CalibrationObject, get_calibration_object
from .cnp_api.cnp_class import (
    DBFileInfo,
    MeasurementListEntries,
    TAsap3Hdl,
    TModulHdl,
    TScriptHdl,
    TTaskInfo2,
    enum_type,
)
from .cnp_api.cnp_constants import DBFileType, DriverType, TAsap3DBOType, TAsap3ECUState
from .cnp_api.cnp_prototype import CANapeDll
from .config import RC
from .ecu_task import EcuTask
from .script import Script


class MeasurementListEntry(NamedTuple):
    task_id: int
    rate: int
    save_flag: bool
    disabled: bool
    object_name: str


class DatabaseInfo(NamedTuple):
    file_name: str
    file_path: str
    file_type: DBFileType


class Module:
    def __init__(
        self,
        dll: CANapeDll,
        asap3_handle: TAsap3Hdl,  # type: ignore[valid-type]
        module_handle: TModulHdl,
    ) -> None:
        """The :class:`~pycanape.module.Module` class is not meant to be instantiated
        by the user. Instead, :class:`~pycanape.module.Module` instances are returned by
        :meth:`~pycanape.canape.CANape.create_module`, :meth:`~pycanape.canape.CANape.get_module_by_index`
        and :meth:`~pycanape.canape.CANape.get_module_by_name`.

        :param asap3_handle:
        :param module_handle:
        """
        self._dll = dll
        self.asap3_handle = asap3_handle
        self.module_handle = module_handle

        self._objects_cache: Optional[List[str]] = None

    def get_database_info(self) -> DatabaseInfo:
        """Get Info concerning the database file."""
        cnp_info = DBFileInfo()
        self._dll.Asap3GetDatabaseInfo(
            self.asap3_handle,
            self.module_handle,
            ctypes.byref(cnp_info),
        )
        db_info = DatabaseInfo(
            file_name=cnp_info.asap2Fname.decode(RC["ENCODING"]),
            file_path=cnp_info.asap2Path.decode(RC["ENCODING"]),
            file_type=DBFileType(cnp_info.type),
        )
        return db_info

    def get_database_path(self) -> str:
        """Get path to database file."""
        db_info = self.get_database_info()
        return os.path.join(db_info.file_path, db_info.file_name)

    def is_module_active(self) -> bool:
        """Return the activation state of the module.

        :return:
            activation state
        """
        active = ctypes.c_bool()
        self._dll.Asap3IsModuleActive(
            self.asap3_handle,
            self.module_handle,
            ctypes.byref(active),
        )
        return active.value

    def module_activation(self, activate: bool = True) -> None:
        """Switches the module activation state.

        :param activate:
            True -> activate Module
            False -> deactivate Module
        """
        self._dll.Asap3ModuleActivation(
            self.asap3_handle,
            self.module_handle,
            activate,
        )

    def is_ecu_online(self) -> bool:
        """Asks CANape whether a ECU is online or offline"""
        ecu_state = enum_type()
        self._dll.Asap3IsECUOnline(
            self.asap3_handle, self.module_handle, ctypes.byref(ecu_state)
        )
        if ecu_state.value == TAsap3ECUState.TYPE_SWITCH_ONLINE:
            return True

        return False

    def switch_ecu_on_offline(self, online: bool, download: bool = True) -> None:
        """Switches an ECU from online to offline and vice versa.

        :param online:
            Switch ECU online if True, switch ECU offline if False
        :param download:
            if this parameter is set to true CANape will
            execute an download in case of online = True
        """
        ecu_state = (
            TAsap3ECUState.TYPE_SWITCH_ONLINE
            if online
            else TAsap3ECUState.TYPE_SWITCH_OFFLINE
        )
        self._dll.Asap3ECUOnOffline(
            self.asap3_handle,
            self.module_handle,
            ecu_state,
            download,
        )

    def get_module_name(self) -> str:
        """Get name of module."""
        buffer = ctypes.c_char_p()
        ptr = ctypes.pointer(buffer)

        self._dll.Asap3GetModuleName(
            self.asap3_handle,
            self.module_handle,
            ptr,
        )
        return buffer.value.decode(RC["ENCODING"])  # type: ignore[union-attr]

    def get_communication_type(self) -> str:
        """Get current communication type (e.g. "CAN")."""
        buffer = ctypes.c_char_p()
        self._dll.Asap3GetCommunicationType(
            self.asap3_handle,
            self.module_handle,
            ctypes.pointer(buffer),
        )
        return buffer.value.decode(RC["ENCODING"])  # type: ignore[union-attr]

    def get_database_objects(self) -> List[str]:
        """Get a list of all object names in database.

        :return:
            List of object names
        """
        if self._objects_cache is None:
            # call function first time to determine max_size
            max_size = ctypes.c_ulong(0)
            self._dll.Asap3GetDatabaseObjects(
                self.asap3_handle,
                self.module_handle,
                None,
                ctypes.byref(max_size),
                TAsap3DBOType.DBTYPE_ALL,
            )

            # call function again to retrieve data
            buffer = ctypes.create_string_buffer(max_size.value)
            self._dll.Asap3GetDatabaseObjects(
                self.asap3_handle,
                self.module_handle,
                buffer,
                ctypes.byref(max_size),
                TAsap3DBOType.DBTYPE_ALL,
            )
            self._objects_cache = (
                buffer.value.strip(b";")[: max_size.value]
                .decode(RC["ENCODING"])
                .split(";")
            )

        return copy.copy(self._objects_cache)

    def get_ecu_tasks(self) -> Dict[str, EcuTask]:
        """Get available data acquisition tasks.

        :return:
            A dictionary with the ecu task description as keys
            and the `EcuTask` instances as values
        """
        task_info_array = (TTaskInfo2 * 32)()
        ptr_task_no = ctypes.pointer(ctypes.c_ushort())
        self._dll.Asap3GetEcuTasks2(
            self.asap3_handle,
            self.module_handle,
            task_info_array,
            ptr_task_no,
            32,
        )
        cnp_task_info_list = [*task_info_array][: ptr_task_no.contents.value]

        def get_task_instance(task_info: TTaskInfo2) -> EcuTask:
            return EcuTask(
                dll=self._dll,
                asap3_handle=self.asap3_handle,
                module_handle=self.module_handle,
                task_info=task_info,
            )

        ecu_task_list = [get_task_instance(ti) for ti in cnp_task_info_list]
        return {et.description: et for et in ecu_task_list}

    def get_network_name(self) -> str:
        """Receives the name of the used network."""
        c_name = ctypes.create_string_buffer(256)
        size = ctypes.c_uint()
        self._dll.Asap3GetNetworkName(
            self.asap3_handle,
            self.module_handle,
            ctypes.cast(ctypes.byref(c_name), ctypes.c_char_p),
            ctypes.byref(size),
        )
        return c_name.value[: size.value].decode(RC["ENCODING"])

    def get_ecu_driver_type(self) -> DriverType:
        """Retrieves the drivertype of an ECU.

        :return:
            DriverType enum
        """
        c_driver_type = enum_type()
        self._dll.Asap3GetEcuDriverType(
            self.asap3_handle,
            self.module_handle,
            ctypes.byref(c_driver_type),
        )
        return DriverType(c_driver_type.value)

    def get_calibration_object(self, name: str) -> CalibrationObject:
        """Get calibration object by name or wildcard pattern (e.g. '\\*InitReset')."""
        if "*" in name:
            filtered = fnmatch.filter(names=self.get_database_objects(), pat=name)
            if len(filtered) == 1:
                name = filtered[0]

        return get_calibration_object(
            dll=self._dll,
            asap3_handle=self.asap3_handle,
            module_handle=self.module_handle,
            name=name,
        )

    def has_resume_mode(self) -> bool:
        """Information about the Resume mode.

        :return:
            Function returns True if the device supports resume mode.
        """
        bln = ctypes.c_bool()
        self._dll.Asap3HasResumeMode(
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
        entries = MeasurementListEntries()
        ptr = ctypes.pointer(ctypes.pointer(entries))
        self._dll.Asap3GetMeasurementListEntries(
            self.asap3_handle,
            self.module_handle,
            ptr,
        )
        entries = ptr.contents[0]

        res = {}
        for idx in range(entries.ItemCount):
            c_entry = entries.Entries[idx][0]
            mle = MeasurementListEntry(
                task_id=c_entry.taskId,
                rate=c_entry.rate,
                save_flag=c_entry.SaveFlag,
                disabled=c_entry.Disabled,
                object_name=c_entry.ObjectName.decode(RC["ENCODING"]),
            )
            res[mle.object_name] = mle
        return res

    def reset_data_acquisition_channels_by_module(self) -> None:
        """Clears the data acquisition channel list of a specific module.

        .. note::
            this function only clears these measurement objects from the
            API-Measurement-List which are defined by API
        """
        self._dll.Asap3ResetDataAcquisitionChnlsByModule(
            self.asap3_handle,
            self.module_handle,
        )

    def release_module(self) -> None:
        self._dll.Asap3ReleaseModule(
            self.asap3_handle,
            self.module_handle,
        )

    def execute_script_ex(self, script_file: bool, script: str) -> Script:
        """Execute a script file or a single script command.

        :param script_file:
            Declares interpretation of parameter script.
            If 'script_file' is true, parameter 'script' is
            interpreted as the file name of the script file
            to be executed. If 'script_file' is false,
            'script' is interpreted as a single script command
        :param script:
            A script filename or a single script command
        :return:
            The instance of the Script class
        """
        script_handle = TScriptHdl()
        self._dll.Asap3ExecuteScriptEx(
            self.asap3_handle,
            self.module_handle,
            script_file,
            script.encode(RC["ENCODING"]),
            ctypes.byref(script_handle),
        )
        return Script(
            dll=self._dll, asap3_handle=self.asap3_handle, script_handle=script_handle
        )
