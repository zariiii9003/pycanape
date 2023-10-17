# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT

import ctypes
import functools
import logging
import sys
from ctypes import wintypes
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Final, TypeVar

from packaging.version import Version

from ..utils import CANapeError
from . import cnp_class, cnp_constants

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec

LOG = logging.getLogger(__name__)

_P1 = ParamSpec("_P1")
_T1 = TypeVar("_T1")


def _synchronize(func: Callable[_P1, _T1]) -> Callable[_P1, _T1]:
    """Use locks to assure thread safety.

    Without synchronization it is possible that Asap3GetLastError
    retrieves the error of the wrong function."""

    def wrapper(*args, **kwargs):
        with CANapeDll.lock:
            return func(*args, **kwargs)

    return wrapper


class CANapeDll:
    lock: Final = RLock()

    def __init__(self, lib_path: Path) -> None:  # noqa: PLR0915
        self.windll = ctypes.WinDLL(str(lib_path))

        # fmt: off
        # ********* these functions must be declared before all others ********
        self.Asap3GetLastError = self._map_symbol(
            func_name="Asap3GetLastError",
            restype=ctypes.c_ushort,
            argtypes=[cnp_class.TAsap3Hdl],             # > TAsap3Hdl hdl
        )
        self.Asap3ErrorText = self._map_symbol(
            func_name="Asap3ErrorText",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_ushort,                        # > unsigned short errCode
                ctypes.POINTER(ctypes.c_char_p),        # < char ** errMsg
            ],
        )
        self.Asap3GetVersion = self._map_symbol(
            func_name="Asap3GetVersion",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.version_t),    # < version_t * version
            ],
            errcheck=self._get_last_error,
        )
        # *********************************************************************

        self.Asap3CalibrationObjectInfoEx = self._map_symbol(
            func_name="Asap3CalibrationObjectInfoEx",
            restype=ctypes.c_bool,
            argtypes=(
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                ctypes.POINTER(ctypes.c_short),         # < short *xDimension
                ctypes.POINTER(ctypes.c_short),         # < short *yDimension
                ctypes.POINTER(cnp_class.enum_type),    # < TValueType *type
            ),
            errcheck=self._get_last_error,
        )

        self.Asap3CheckOverrun = self._map_symbol(
            func_name="Asap3CheckOverrun",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_ushort,                        # > unsigned short taskId
                ctypes.c_bool,                          # > bool resetOverrun
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CreateDevice = self._map_symbol(
            func_name="Asap3CreateDevice",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char* moduleName
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
                ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl* module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CreateModule = self._map_symbol(
            func_name="Asap3CreateModule",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char * moduleName
                ctypes.c_char_p,                        # > const char * databaseFilename
                ctypes.c_short,                         # > short driverType
                ctypes.c_short,                         # > short channelNo
                ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl * module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CreateModule3 = self._map_symbol(
            func_name="Asap3CreateModule3",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *moduleName
                ctypes.c_char_p,                        # > const char *databaseFilename
                ctypes.c_short,                         # > short driverType
                ctypes.c_short,                         # > short channelNo
                ctypes.c_bool,                          # > bool goOnline
                ctypes.c_short,                         # > short enablecache
                ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl * module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CreateParameterTemplate = self._map_symbol(
            func_name="Asap3CreateParameterTemplate",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(cnp_class.TParamTemplateHdl),  # < TParamTemplateHdl* paramHandle
                ctypes.c_char_p,                        # > char* name = nullptr
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CreateSBLConfiguration = self._map_symbol(
            func_name="Asap3CreateSBLConfiguration",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char* ipAdress
                ctypes.c_int,                           # > int port = 9815
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DefineRecorder = self._map_symbol(
            func_name="Asap3DefineRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *RecorderName
                ctypes.POINTER(cnp_class.TRecorderID),  # < TRecorderID * trecorder
                cnp_class.enum_type,                    # > TRecorderType RecorderType=eTRecorderTypeMDF
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ECUOnOffline = self._map_symbol(
            func_name="Asap3ECUOnOffline",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                cnp_class.enum_type,                    # > TAsap3ECUState State
                ctypes.c_bool,                          # > bool download
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3EnableRecorder = self._map_symbol(
            func_name="Asap3EnableRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_bool,                          # > bool enable
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3EnumInterfaceNames = self._map_symbol(
            func_name="Asap3EnumInterfaceNames",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.enum_type,                    # > TLogicalChannels protocoltype
                ctypes.c_uint,                          # > unsigned int index
                ctypes.POINTER(ctypes.c_char_p),        # < char ** CANpName
                ctypes.POINTER(ctypes.c_char_p),        # < char** PhysInterfacename
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3Exit2 = self._map_symbol(
            func_name="Asap3Exit2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_bool,                          # > bool close_CANape
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3FindParameterTemplate = self._map_symbol(
            func_name="Asap3FindParameterTemplate",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char* Name
                ctypes.POINTER(cnp_class.TParamTemplateHdl),  # < TParamTemplateHdl* paramHandle
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetApplicationSettings = self._map_symbol(
            func_name="Asap3GetApplicationSettings",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char* Keyname
                ctypes.POINTER(cnp_class.TSettingsParam),  # > TSettingsParam* ResponseData
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetApplicationVersion = self._map_symbol(
            func_name="Asap3GetApplicationVersion",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(cnp_class.Appversion),   # < Appversion * version
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetCNAFilename = self._map_symbol(
            func_name="Asap3GetCNAFilename",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_char),          # > char *FileName
                ctypes.POINTER(wintypes.UINT),          # > unsigned int *Size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetCommunicationType = self._map_symbol(
            func_name="Asap3GetCommunicationType",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_char_p),        # < char ** commType
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetCurrentValues = self._map_symbol(
            func_name="Asap3GetCurrentValues",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl _module
                ctypes.c_ushort,                        # > unsigned short taskId
                ctypes.POINTER(cnp_class.TTime),        # < ::TTime * timeStamp
                ctypes.POINTER(ctypes.c_double),        # < double * values
                ctypes.c_ushort,                        # > unsigned short maxValues
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetDatabaseInfo = self._map_symbol(
            func_name="Asap3GetDatabaseInfo",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(cnp_class.DBFileInfo),   # < DBFileInfo *Info
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetDBObjectInfo = self._map_symbol(
            func_name="Asap3GetDBObjectInfo",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char *ObjectName
                ctypes.POINTER(cnp_class.DBObjectInfo),  # < DBObjectInfo *Info
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetDatabaseObjects = self._map_symbol(
            func_name="Asap3GetDatabaseObjects",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_char),          # > char *DataObjects
                ctypes.POINTER(wintypes.UINT),          # > UINT *MaxSize
                cnp_class.enum_type,                    # > TAsap3DBOType DbType
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetEcuDriverType = self._map_symbol(
            func_name="Asap3GetEcuDriverType",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(cnp_class.enum_type),    # < tDriverType *DriverType
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetEcuTasks = self._map_symbol(
            func_name="Asap3GetEcuTasks2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(cnp_class.TTaskInfo),    # < TTaskInfo * taskInfo
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short *noTasks
                ctypes.c_short,                         # > unsigned short maxTaskInfo
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetEcuTasks2 = self._map_symbol(
            func_name="Asap3GetEcuTasks2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(cnp_class.TTaskInfo2),   # < TTaskInfo2 * taskInfo2
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short *noTasks
                ctypes.c_short,                         # > unsigned short maxTaskInfo
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetFifoLevel = self._map_symbol(
            func_name="Asap3GetFifoLevel",
            restype=ctypes.c_long,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_ushort,                        # > unsigned short taskId
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetInterfaceNames = self._map_symbol(
            func_name="Asap3GetInterfaceNames",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.enum_type,                    # > TLogicalChannels protocoltype
                ctypes.POINTER(ctypes.c_int),           # < int *Count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetMeasurementListEntries = self._map_symbol(
            func_name="Asap3GetMeasurementListEntries",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.POINTER(cnp_class.MeasurementListEntries)),  # < MeasurementListEntries **Items
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetMeasurementState = self._map_symbol(
            func_name="Asap3GetMeasurementState",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(cnp_class.enum_type),    # > tMeasurementState *State
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetModuleCount = self._map_symbol(
            func_name="Asap3GetModuleCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetModuleHandle = self._map_symbol(
            func_name="Asap3GetModuleHandle",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *moduleName
                ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl * module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetModuleName = self._map_symbol(
            func_name="Asap3GetModuleName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_char_p),        # < char **moduleName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetNetworkName = self._map_symbol(
            func_name="Asap3GetNetworkName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # < char *Name
                ctypes.POINTER(ctypes.c_uint),          # < unsigned int * sizeofName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetNextSample = self._map_symbol(
            func_name="Asap3GetNextSample",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_ushort,                        # > unsigned short taskId
                ctypes.POINTER(cnp_class.TTime),        # < TTime * timeStamp
                ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),  # < double ** values
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetParameterCount = self._map_symbol(
            func_name="Asap3GetParameterCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short* count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetParameterInfoByClass = self._map_symbol(
            func_name="Asap3GetParameterInfoByClass",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.enum_type,                    # > eTParameterClass type
                ctypes.POINTER(cnp_class.enum_type),    # < eTSettingsParameterType* settingstype
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short* maxsize
                ctypes.POINTER(ctypes.c_char_p),        # < char ** name
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetParameterInfoByIndex = self._map_symbol(
            func_name="Asap3GetParameterInfoByIndex",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_uint,                          # > unsigned int index
                ctypes.POINTER(cnp_class.enum_type),    # < eTParameterClass* type
                ctypes.POINTER(cnp_class.enum_type),    # < eTSettingsParameterType* settingstype
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short* maxsize
                ctypes.POINTER(ctypes.c_char_p),        # < char ** name
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetParameterInfoByClassName = self._map_symbol(
            func_name="Asap3GetParameterInfoByClassName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char* classname
                ctypes.POINTER(cnp_class.enum_type),    # < eTParameterClass* type
                ctypes.POINTER(cnp_class.enum_type),    # < eTSettingsParameterType* settingstype
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short* maxsize
                ctypes.POINTER(ctypes.c_char_p),        # < char ** name
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetParameterTemplateName = self._map_symbol(
            func_name="Asap3GetParameterTemplateName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
                ctypes.POINTER(ctypes.c_char_p),        # < char** Name
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetProjectDirectory = self._map_symbol(
            func_name="Asap3GetProjectDirectory",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # < char* directory
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetRecorderByIndex = self._map_symbol(
            func_name="Asap3GetRecorderByIndex",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_ulong,                         # > unsigned long index
                ctypes.POINTER(cnp_class.TRecorderID),  # < TRecorderID *recorderID
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetRecorderCount = self._map_symbol(
            func_name="Asap3GetRecorderCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetRecorderMdfFileName = self._map_symbol(
            func_name="Asap3GetRecorderMdfFileName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_char_p,                        # < char *FileName
                ctypes.POINTER(wintypes.DWORD),         # < DWORD *size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetRecorderName = self._map_symbol(
            func_name="Asap3GetRecorderName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_char_p,                        # < char * recorderName
                ctypes.POINTER(ctypes.c_long),          # < long *Size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetRecorderState = self._map_symbol(
            func_name="Asap3GetRecorderState",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.POINTER(cnp_class.enum_type),    # < EnRecorderState *State
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetSelectedRecorder = self._map_symbol(
            func_name="Asap3GetSelectedRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(cnp_class.TRecorderID),  # < TRecorderID *recorderID
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetTemplateParameterByIndex = self._map_symbol(
            func_name="Asap3GetTemplateParameterByIndex",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
                ctypes.c_uint,                          # > unsigned int index
                ctypes.POINTER(cnp_class.enum_type),    # < eTParameterClass type
                ctypes.POINTER(cnp_class.enum_type),    # < eTSettingsParameterType* settingstype
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short* maxsize
                ctypes.POINTER(ctypes.c_void_p),        # < void** data
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetTemplateParameterCount = self._map_symbol(
            func_name="Asap3GetTemplateParameterCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long* count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetTemplateParameterInfo = self._map_symbol(
            func_name="Asap3GetTemplateParameterInfo",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
                ctypes.POINTER(cnp_class.enum_type),    # < eTParameterClass type
                ctypes.POINTER(cnp_class.enum_type),    # < eTSettingsParameterType* settingstype
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short* maxsize
                ctypes.POINTER(ctypes.c_void_p),        # < void** data
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3HasMCD3License = self._map_symbol(
            func_name="Asap3HasMCD3License",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_bool),          # < bool *available
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3HasResumeMode = self._map_symbol(
            func_name="Asap3HasResumeMode",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_bool),          # < bool *possible
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3Init5 = self._map_symbol(
            func_name="Asap3Init5",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.TAsap3Hdl),    # < TAsap3Hdl * hdl,
                ctypes.c_ulong,                         # > unsigned long responseTimeout,
                ctypes.c_char_p,                        # > const char *workingDir,
                ctypes.c_ulong,                         # > unsigned long fifoSize,
                ctypes.c_ulong,                         # > unsigned long sampleSize,
                ctypes.c_bool,                          # > bool debugMode,
                ctypes.c_bool,                          # > bool clearDeviceList,
                ctypes.c_bool,                          # > bool bHexmode,
                ctypes.c_bool,                          # > bool bModalMode
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsECUOnline = self._map_symbol(
            func_name="Asap3IsECUOnline",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(cnp_class.enum_type),    # < TAsap3ECUState *State
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsModuleActive = self._map_symbol(
            func_name="Asap3IsModuleActive",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_bool),          # < bool *activate
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsNetworkActivated = self._map_symbol(
            func_name="Asap3IsNetworkActivated",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *Name
                ctypes.POINTER(ctypes.c_bool),          # < bool *activated
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsRecorderEnabled = self._map_symbol(
            func_name="Asap3IsRecorderEnabled",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.POINTER(ctypes.c_bool),          # < bool *enabled
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsValidParameterTemplate = self._map_symbol(
            func_name="Asap3IsValidParameterTemplate",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3LoadCNAFile = self._map_symbol(
            func_name="Asap3LoadCNAFile",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char* configFileName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ModuleActivation = self._map_symbol(
            func_name="Asap3ModuleActivation",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_bool,                          # > bool activate
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3PauseRecorder = self._map_symbol(
            func_name="Asap3PauseRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_bool,                          # > bool Pause
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3PopupDebugWindow = self._map_symbol(
            func_name="Asap3PopupDebugWindow",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ]
        )

        self.Asap3ReadCalibrationObject2 = self._map_symbol(
            func_name="Asap3ReadCalibrationObject2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.c_bool,                          # > bool forceupload
                ctypes.POINTER(cnp_class.TCalibrationObjectValue),  # < TCalibrationObjectValue *value
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ReadObjectParameter = self._map_symbol(
            func_name="Asap3ReadObjectParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *objectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.POINTER(cnp_class.enum_type),    # < TAsap3DataType * type
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long * address
                ctypes.POINTER(ctypes.c_double),        # < double * min
                ctypes.POINTER(ctypes.c_double),        # < double * max
                ctypes.POINTER(ctypes.c_double),        # < double * increment
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3RegisterCallBack = self._map_symbol(
            func_name="Asap3RegisterCallBack",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.enum_type,                    # > ASAP3_EVENT_CODE eventID
                cnp_class.EVENT_CALLBACK,               # > void *fnc
                ctypes.c_ulong,                         # > unsigned long privateData
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ReleaseInterfaceNames = self._map_symbol(
            func_name="Asap3ReleaseInterfaceNames",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.enum_type,                    # > TLogicalChannels protocoltype
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ReleaseModule = self._map_symbol(
            func_name="Asap3ReleaseModule",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ReleaseParameterTemplate = self._map_symbol(
            func_name="Asap3ReleaseParameterTemplate",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ReleaseTemplateParameterItem = self._map_symbol(
            func_name="Asap3ReleaseTemplateParameterItem",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
                cnp_class.enum_type,                    # > eTParameterClass type
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ResetDataAcquisitionChnls = self._map_symbol(
            func_name="Asap3ResetDataAcquisitionChnls",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ResetDataAcquisitionChnlsByModule = self._map_symbol(
            func_name="Asap3ResetDataAcquisitionChnlsByModule",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl hmod
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetInteractiveMode = self._map_symbol(
            func_name="Asap3SetInteractiveMode",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_bool,                          # > bool mode
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetTemplateParameterItem = self._map_symbol(
            func_name="Asap3SetTemplateParameterItem",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TParamTemplateHdl,            # > TParamTemplateHdl paramHandle
                cnp_class.enum_type,                    # > eTParameterClass type
                ctypes.c_void_p,                        # > void* data
                ctypes.c_ushort,                        # > unsigned short sizeofdata
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetRecorderMdfFileName = self._map_symbol(
            func_name="Asap3SetRecorderMdfFileName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_char_p,                        # > char *FileName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetTCPOptions = self._map_symbol(
            func_name="Asap3SetTCPOptions",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.c_char_p,                        # > const char* ipAddress
                ctypes.c_ulong,                         # > unsigned long portNumber
            ],
        )

        self.Asap3SetupDataAcquisitionChnl = self._map_symbol(
            func_name="Asap3SetupDataAcquisitionChnl",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *measurementObjectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.c_ushort,                        # > unsigned short taskId
                ctypes.c_short,                         # > unsigned short pollingRate
                ctypes.c_bool,                          # > bool save2File
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StartDataAcquisition = self._map_symbol(
            func_name="Asap3StartDataAcquisition",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StartRecorder = self._map_symbol(
            func_name="Asap3StartRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StopRecorder = self._map_symbol(
            func_name="Asap3StopRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_bool,                          # > bool save2Mdf
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StopDataAcquisition = self._map_symbol(
            func_name="Asap3StopDataAcquisition",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3TestObject = self._map_symbol(
            func_name="Asap3TestObject",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char * objectName
                ctypes.POINTER(cnp_class.enum_type),    # < TObjectType * type
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3WriteCalibrationObject = self._map_symbol(
            func_name="Asap3WriteCalibrationObject",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.POINTER(cnp_class.TCalibrationObjectValue),  # > TCalibrationObjectValue * value
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ExecuteScriptEx = self._map_symbol(
            func_name="Asap3ExecuteScriptEx",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_bool,                          # > bool scriptFile
                ctypes.c_char_p,                        # > const char *script
                ctypes.POINTER(cnp_class.TScriptHdl),   # < TScriptHdl *hScript
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetScriptResultString = self._map_symbol(
            func_name="Asap3GetScriptResultString",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
                ctypes.POINTER(ctypes.c_char),          # < char *resultString
                ctypes.POINTER(ctypes.c_ulong),         # < DWORD *sizeofBuffer
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetScriptResultValue = self._map_symbol(
            func_name="Asap3GetScriptResultValue",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
                ctypes.POINTER(ctypes.c_double),        # < double *Value
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetScriptState = self._map_symbol(
            func_name="Asap3GetScriptState",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
                ctypes.POINTER(cnp_class.enum_type),    # < TScriptStatus *scrstate
                ctypes.POINTER(ctypes.c_char),          # < char *textBuffer
                ctypes.POINTER(ctypes.c_ulong),         # < DWORD *sizeofBuffer
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ReleaseScript = self._map_symbol(
            func_name="Asap3ReleaseScript",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StartScript = self._map_symbol(
            func_name="Asap3StartScript",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
                ctypes.c_char_p,                        # > char *  Commandline = NULL
                cnp_class.TModulHdl,                    # > TModulHdl  moduleHdl = ASAP3_INVALID_MODULE_HDL
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StopScript = self._map_symbol(
            func_name="Asap3StopScript",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
            ],
            errcheck=self._get_last_error,
        )

    # fmt: on

    @property
    def version(self) -> Version:
        _dll_version = cnp_class.version_t()
        self.Asap3GetVersion(ctypes.byref(_dll_version))
        return Version(
            f"{_dll_version.dllMainVersion}"
            f".{_dll_version.dllSubVersion}"
            f".{_dll_version.dllRelease}"
        )

    def _get_last_error(self, result, function, args):
        if result:
            return args

        handle = args[0].contents if hasattr(args[0], "contents") else args[0]

        error_code = self.Asap3GetLastError(handle)
        buffer = ctypes.c_char_p()
        ptr = ctypes.pointer(buffer)

        self.Asap3ErrorText(
            handle,
            error_code,
            ptr,
        )

        if error_code > 0:
            error_msg = (
                f"{cnp_constants.ErrorCodes(error_code).name}: "  # type: ignore[union-attr]
                f"{ptr.contents.value.decode('ascii')}"
            )
            raise CANapeError(error_code, error_msg, function.__name__)
        return args

    def _map_symbol(  # type: ignore[no-untyped-def]
        self,
        func_name: str,
        restype=None,
        argtypes=(),
        errcheck=None,
    ) -> Callable[..., Any]:
        """
        Map and return a symbol (function) from a C library. A reference to the
        mapped symbol is also held in the instance
        :param str func_name:
            symbol_name
        :param ctypes.c_* restype:
            function result type (i.e. ctypes.c_ulong...), defaults to void
        :param tuple(ctypes.c_* ... ) argtypes:
            argument types, defaults to no args
        :param callable errcheck:
            optional error checking function, see ctypes docs for _FuncPtr
        """
        if argtypes:
            prototype = ctypes.WINFUNCTYPE(restype, *argtypes)
        else:
            prototype = ctypes.WINFUNCTYPE(restype)
        try:
            symbol = prototype((func_name, self.windll))
        except AttributeError:
            warning_msg = (
                f"Could not map function '{func_name}' to library {self.windll._name}"
            )
            LOG.warning(warning_msg)
            # the function is not available, replace it with another function, that will raise a `NotImplementedError`
            symbol = functools.partial(self._not_implemented, func_name, self.version)  # type: ignore[assignment]
        else:
            symbol.__name__ = func_name  # type: ignore[attr-defined]

            if errcheck:
                symbol.errcheck = errcheck

        func = _synchronize(symbol)

        setattr(self, func_name, func)
        return func

    @staticmethod
    def _not_implemented(
        func_name: str, dll_version: Version, *_args: Any, **_kwargs: Any
    ) -> None:
        err_msg = f"The function '{func_name}' was not found in CANape DLL version {dll_version}."
        raise NotImplementedError(err_msg)
