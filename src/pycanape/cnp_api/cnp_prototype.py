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

LOG = logging.getLogger("pycanape")

_P1 = ParamSpec("_P1")
_T1 = TypeVar("_T1")


def _synchronize(func: Callable[_P1, _T1]) -> Callable[_P1, _T1]:
    """Use locks to assure thread safety.

    Without synchronization, it is possible that Asap3GetLastError
    retrieves the error of the wrong function."""

    def wrapper(*args: _P1.args, **kwargs: _P1.kwargs) -> _T1:
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

        self.Asap3ActivateNetwork = self._map_symbol(
            func_name="Asap3ActivateNetwork",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *Name
                ctypes.c_bool,                          # > bool activate
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3AddItemToRecorder = self._map_symbol(
            func_name="Asap3AddItemToRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const  char* MeasurementObject
                cnp_class.TRecorderID,                  # > TRecorderID RecorderID
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3AddSecProfileToNetwork = self._map_symbol(
            func_name="Asap3AddSecProfileToNetwork",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_uint,                          # > unsigned int profileId
                ctypes.c_char_p,                        # > char* networkName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3AttachAsap2 = self._map_symbol(
            func_name="Asap3AttachAsap2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *asap2Fname
                ctypes.c_short,                         # > short canChnl
                ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl * module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CalibrationObjectInfo = self._map_symbol(
            func_name="Asap3CalibrationObjectInfo",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                ctypes.POINTER(ctypes.c_short),         # < short * xDimension
                ctypes.POINTER(ctypes.c_short),         # < short * yDimension
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CalibrationObjectInfoEx = self._map_symbol(
            func_name="Asap3CalibrationObjectInfoEx",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                ctypes.POINTER(ctypes.c_short),         # < short *xDimension
                ctypes.POINTER(ctypes.c_short),         # < short *yDimension
                ctypes.POINTER(cnp_class.enum_type),    # < TValueType *type
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CalibrationObjectRecordInfo = self._map_symbol(
            func_name="Asap3CalibrationObjectRecordInfo",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                ctypes.POINTER(cnp_class.TLayoutCoeffs),  # < TLayoutCoeffs * coeffs
                ctypes.POINTER(ctypes.c_short),         # < short * xDimension
                ctypes.POINTER(ctypes.c_short),         # < short * yDimension
            ],
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

        self.Asap3ClearResumeMode = self._map_symbol(
            func_name="Asap3ClearResumeMode",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ConnectDataAcquisition = self._map_symbol(
            func_name="Asap3ConnectDataAcquisition",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ConnectToCANape = self._map_symbol(
            func_name="Asap3ConnectToCANape",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.TAsap3Hdl),    # < TAsap3Hdl *hdl
                ctypes.c_char_p,                        # > const char *VillaRelease
                ctypes.c_char_p,                        # > const char *Directory
                ctypes.c_char_p,                        # > const char *language
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CopyBinaryFile = self._map_symbol(
            func_name="Asap3CopyBinaryFile",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                cnp_class.enum_type,                    # > TAsap3FileType sourcetype
                cnp_class.enum_type,                    # > TAsap3FileType desttype
                ctypes.c_char_p,                        # > const char *filename
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

        self.Asap3CreateLoggerConfiguration = self._map_symbol(
            func_name="Asap3CreateLoggerConfiguration",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
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

        self.Asap3CreateModule2 = self._map_symbol(
            func_name="Asap3CreateModule2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *moduleName
                ctypes.c_char_p,                        # > const char *databaseFilename
                ctypes.c_short,                         # > short driverType
                ctypes.c_short,                         # > short channelNo
                ctypes.c_bool,                          # > bool goOnline
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

        self.Asap3CreateModule4 = self._map_symbol(
            func_name="Asap3CreateModule4",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char* moduleName
                ctypes.c_char_p,                        # > const char* databaseFname
                ctypes.c_short,                         # > short driverType
                ctypes.c_short,                         # > short channelNo
                ctypes.c_char_p,                        # > const char* interfaceName
                ctypes.c_bool,                          # > bool goOnline
                ctypes.c_short,                         # > short enableCache
                ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl* module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3CreateModuleSec = self._map_symbol(
            func_name="Asap3CreateModuleSec",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char* moduleName
                ctypes.c_char_p,                        # > const char* databaseFname
                ctypes.c_short,                         # > short driverType
                ctypes.c_short,                         # > short channelNo
                ctypes.c_char_p,                        # > const char* interfaceName
                ctypes.c_uint,                          # > unsigned int secProfileId
                ctypes.c_char_p,                        # > const char* securityRole
                ctypes.c_bool,                          # > bool goOnline
                ctypes.c_short,                         # > short enableCache
                ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl* module
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

        self.Asap3DiagCreateRawRequest = self._map_symbol(
            func_name="Asap3DiagCreateRawRequest",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(wintypes.BYTE),          # < BYTE *ServiceBytes
                ctypes.c_uint,                          # > unsigned int length
                ctypes.POINTER(cnp_class.TAsap3DiagHdl),  # < TAsap3DiagHdl *hDiag
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagCreateRawRequest2 = self._map_symbol(
            func_name="Asap3DiagCreateRawRequest2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(wintypes.BYTE),          # < BYTE *Bytes
                ctypes.c_uint,                          # > unsigned int length
                ctypes.POINTER(cnp_class.TAsap3DiagHdl),  # < TAsap3DiagHdl *hDiag
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagCreateSymbolicRequest = self._map_symbol(
            func_name="Asap3DiagCreateSymbolicRequest",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char *ServiceName
                ctypes.POINTER(cnp_class.TAsap3DiagHdl),  # < TAsap3DiagHdl *hDiag
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagEnableTesterPresent = self._map_symbol(
            func_name="Asap3DiagEnableTesterPresent",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_bool,                          # > bool enable
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagExecute = self._map_symbol(
            func_name="Asap3DiagExecute",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                wintypes.BOOL,                          # > BOOL SupressPositiveResponse
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagExecuteJob = self._map_symbol(
            func_name="Asap3DiagExecuteJob",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char *job
                ctypes.c_char_p,                        # > char *commandline
                ctypes.c_bool,                          # > bool reserved
                ctypes.POINTER(ctypes.POINTER(cnp_class.DiagJobResponse)),  # < DiagJobResponse** jobResponse
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetComplexIterationCount = self._map_symbol(
            func_name="Asap3DiagGetComplexIterationCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char *Parameter
                ctypes.c_long,                          # > long ResponseID
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *Iteration
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetComplexNumericResponseParameter = self._map_symbol(
            func_name="Asap3DiagGetComplexNumericResponseParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char *name
                ctypes.c_long,                          # > long ResponseID
                ctypes.c_char_p,                        # > char *SubParameter
                ctypes.c_ulong,                         # > unsigned long InterationIndex
                ctypes.POINTER(cnp_class.DiagNumericParameter),  # < DiagNumericParameter *Parameter
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetComplexRawResponseParameter = self._map_symbol(
            func_name="Asap3DiagGetComplexRawResponseParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char *name
                ctypes.c_long,                          # > long ResponseID
                ctypes.c_char_p,                        # > char *SubParameter
                ctypes.c_ulong,                         # > unsigned long InterationIndex
                ctypes.c_char_p,                        # > char *Data
                ctypes.POINTER(wintypes.DWORD),         # < DWORD *Size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetComplexStringResponseParameter = self._map_symbol(
            func_name="Asap3DiagGetComplexStringResponseParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char *name
                ctypes.c_long,                          # > long ResponseID
                ctypes.c_char_p,                        # > char *SubParameter
                ctypes.c_ulong,                         # > unsigned long InterationIndex
                ctypes.c_char_p,                        # > char *Data
                ctypes.POINTER(wintypes.DWORD),         # < DWORD *Size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetNumericResponseParameter = self._map_symbol(
            func_name="Asap3DiagGetNumericResponseParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char *name
                ctypes.c_long,                          # > long ResponseID
                ctypes.POINTER(cnp_class.DiagNumericParameter),  # < DiagNumericParameter *
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetRawResponseParameter = self._map_symbol(
            func_name="Asap3DiagGetRawResponseParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char *name
                ctypes.c_long,                          # > long ResponseID
                ctypes.POINTER(ctypes.c_ubyte),         # < unsigned char *Data
                ctypes.POINTER(wintypes.DWORD),         # < DWORD *Size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetResponseCode = self._map_symbol(
            func_name="Asap3DiagGetResponseCode",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_long,                          # > long ResponseID
                ctypes.POINTER(wintypes.BYTE),          # < BYTE *Code
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetResponseCount = self._map_symbol(
            func_name="Asap3DiagGetResponseCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.POINTER(ctypes.c_uint),          # < unsigned int *Count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetResponseStream = self._map_symbol(
            func_name="Asap3DiagGetResponseStream",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.POINTER(wintypes.BYTE),          # < BYTE* Stream
                ctypes.POINTER(wintypes.DWORD),         # < DWORD *Size
                ctypes.c_long,                          # > long ResponseID
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetServiceState = self._map_symbol(
            func_name="Asap3DiagGetServiceState",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.POINTER(cnp_class.enum_type),    # < eServiceStates *State
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagGetStringResponseParameter = self._map_symbol(
            func_name="Asap3DiagGetStringResponseParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char *name
                ctypes.c_long,                          # > long ResponseID
                ctypes.c_char_p,                        # > char *Data
                ctypes.POINTER(wintypes.DWORD),         # < DWORD *Size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagIsComplexResponseParameter = self._map_symbol(
            func_name="Asap3DiagIsComplexResponseParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char *name
                ctypes.c_long,                          # > long ResponseID
                ctypes.POINTER(wintypes.BOOL),          # < BOOL *IsComplex
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagIsPositiveResponse = self._map_symbol(
            func_name="Asap3DiagIsPositiveResponse",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_long,                          # > long ResponseID
                ctypes.POINTER(wintypes.BOOL),          # < BOOL *IsPositive
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagIsTesterPresentEnabled = self._map_symbol(
            func_name="Asap3DiagIsTesterPresentEnabled",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_bool),          # < bool *enabled
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagReleaseService = self._map_symbol(
            func_name="Asap3DiagReleaseService",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagSetNotificationParameters = self._map_symbol(
            func_name="Asap3DiagSetNotificationParameters",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                cnp_class.FNCDIAGNOFIFICATION,          # > FNCDIAGNOFIFICATION CallbackFunction
                ctypes.c_void_p,                        # > void *PrivateData
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagSetNumericParameter = self._map_symbol(
            func_name="Asap3DiagSetNumericParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char* ParameterName
                ctypes.POINTER(cnp_class.DiagNumericParameter),  # < DiagNumericParameter *Parameter
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagSetRawParameter = self._map_symbol(
            func_name="Asap3DiagSetRawParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char* ParameterName
                ctypes.POINTER(wintypes.BYTE),          # < BYTE* ParameterValue
                wintypes.DWORD,                         # > DWORD Size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DiagSetStringParameter = self._map_symbol(
            func_name="Asap3DiagSetStringParameter",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TAsap3DiagHdl,                # > TAsap3DiagHdl hDiag
                ctypes.c_char_p,                        # > char* ParameterName
                ctypes.c_char_p,                        # > char* ParameterValue
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DisconnectDataAcquisition = self._map_symbol(
            func_name="Asap3DisconnectDataAcquisition",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3DisconnectFromCANape = self._map_symbol(
            func_name="Asap3DisconnectFromCANape",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
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

        self.Asap3ECUOnOffline2 = self._map_symbol(
            func_name="Asap3ECUOnOffline2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                cnp_class.enum_type,                    # > TAsap3ECUState State
                cnp_class.enum_type,                    # > TeSyncOption  syncaction
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3EnableBusLoggingRecorderByModule = self._map_symbol(
            func_name="Asap3EnableBusLoggingRecorderByModule",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                cnp_class.TModulHdl,                    # > TModulHdl module
                wintypes.BOOL,                          # > BOOL enable
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3EnableBusLoggingRecorderByNetWork = self._map_symbol(
            func_name="Asap3EnableBusLoggingRecorderByNetWork",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_char_p,                        # > char* NetworkName
                wintypes.BOOL,                          # > BOOL enable
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

        self.Asap3ExecuteScript = self._map_symbol(
            func_name="Asap3ExecuteScript",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_bool,                          # > bool scriptFile
                ctypes.c_char_p,                        # > const char * script
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
                ctypes.c_char_p,                        # > const char * script
                ctypes.POINTER(cnp_class.TScriptHdl),   # < TScriptHdl *hScript
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3Exit = self._map_symbol(
            func_name="Asap3Exit",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
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

        self.Asap3FlashGetJobCount = self._map_symbol(
            func_name="Asap3FlashGetJobCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *Count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3FlashGetJobName = self._map_symbol(
            func_name="Asap3FlashGetJobName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_ulong,                         # > unsigned long index
                ctypes.c_char_p,                        # > char *Name
                ctypes.POINTER(ctypes.c_long),          # < long *SizeOfName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3FlashGetJobState = self._map_symbol(
            func_name="Asap3FlashGetJobState",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_double),        # < double *ScriptResult
                ctypes.POINTER(wintypes.BOOL),          # < BOOL *isRunning
                ctypes.POINTER(ctypes.c_long),          # < long *Progress
                ctypes.c_char_p,                        # > char *Info
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *SizeofInfo
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3FlashGetSessionCount = self._map_symbol(
            func_name="Asap3FlashGetSessionCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *Count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3FlashGetSessionName = self._map_symbol(
            func_name="Asap3FlashGetSessionName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_ulong,                         # > unsigned long index
                ctypes.c_char_p,                        # > char *Name
                ctypes.POINTER(ctypes.c_long),          # < long *SizeOfName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3FlashSetODXContainer = self._map_symbol(
            func_name="Asap3FlashSetODXContainer",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *ODXContainerfile
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3FlashStartFlashJob = self._map_symbol(
            func_name="Asap3FlashStartFlashJob",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *SessionName
                ctypes.c_char_p,                        # > const char *JobName
                ctypes.c_char_p,                        # > const char *ConfigFileName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3FlashStopJob = self._map_symbol(
            func_name="Asap3FlashStopJob",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetApplicationName = self._map_symbol(
            func_name="Asap3GetApplicationName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *Name
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *Size
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
                ctypes.POINTER(cnp_class.TSettingsParam),  # < TSettingsParam* ResponseData
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

        self.Asap3GetAsap2 = self._map_symbol(
            func_name="Asap3GetAsap2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_char_p),        # < char ** asap2Fname
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetCANapeMode = self._map_symbol(
            func_name="Asap3GetCANapeMode",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(cnp_class.TCANapeModes),  # < tCANapeModes* modes
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetCNAFilename = self._map_symbol(
            func_name="Asap3GetCNAFilename",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_char),          # > char *FileName
                ctypes.POINTER(ctypes.c_uint),          # < unsigned int *Size
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetCanapeModuleParam = self._map_symbol(
            func_name="Asap3GetCanapeModuleParam",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char *param
                ctypes.c_char_p,                        # > char *value
                ctypes.POINTER(ctypes.c_uint),          # < unsigned int *sizeofValue
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetCanapeProjectParam = self._map_symbol(
            func_name="Asap3GetCanapeProjectParam",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *Section
                ctypes.c_char_p,                        # > char *param
                ctypes.c_char_p,                        # > char *value
                ctypes.POINTER(ctypes.c_uint),          # < unsigned int *sizeofValue
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetChnlDefaultRaster = self._map_symbol(
            func_name="Asap3GetChnlDefaultRaster",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *measurementObjectName
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short *taskId
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short *downSampling
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

        self.Asap3GetDBObjectComment = self._map_symbol(
            func_name="Asap3GetDBObjectComment",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl mod
                ctypes.c_char_p,                        # > char* DBObjname
                ctypes.c_char_p,                        # > char* Comment
                ctypes.POINTER(wintypes.UINT),          # < UINT* size
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

        self.Asap3GetDBObjectUnit = self._map_symbol(
            func_name="Asap3GetDBObjectUnit",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char *DatabaseObjectName
                ctypes.c_char_p,                        # > char *UnitName
                ctypes.POINTER(wintypes.UINT),          # < UINT *Size
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

        self.Asap3GetDatabaseObjects = self._map_symbol(
            func_name="Asap3GetDatabaseObjects",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_char),          # > char *DataObjects
                ctypes.POINTER(wintypes.UINT),          # < UINT *MaxSize
                cnp_class.enum_type,                    # > TAsap3DBOType DbType
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetDatabaseObjectsByType = self._map_symbol(
            func_name="Asap3GetDatabaseObjectsByType",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char *DataObjects
                ctypes.POINTER(wintypes.UINT),          # < UINT *MaxSize
                cnp_class.enum_type,                    # > TAsap3DBOType DbType
                ctypes.c_ulong,                         # > unsigned long TypeFilter
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
            func_name="Asap3GetEcuTasks",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(cnp_class.TTaskInfo),    # < TTaskInfo * taskInfo
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short * noTasks
                ctypes.c_ushort,                        # > unsigned short maxTaskInfo
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
                ctypes.c_ushort,                        # > unsigned short maxTaskInfo
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
        )

        self.Asap3GetInteractiveMode = self._map_symbol(
            func_name="Asap3GetInteractiveMode",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_bool),          # < bool *mode
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

        self.Asap3GetItemRecorderList = self._map_symbol(
            func_name="Asap3GetItemRecorderList",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const  char* MeasurementObject
                ctypes.POINTER(ctypes.c_int),           # < int* count
                ctypes.POINTER(cnp_class.TRecorderID),  # < TRecorderID* RecorderIDList
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetLastError = self._map_symbol(
            func_name="Asap3GetLastError",
            restype=ctypes.c_short,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ],
        )

        self.Asap3GetMdfFilename = self._map_symbol(
            func_name="Asap3GetMdfFilename",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_char_p),        # < char ** mdfFilename
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
                ctypes.POINTER(cnp_class.enum_type),    # < tMeasurementState *State
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetMemoryPage = self._map_symbol(
            func_name="Asap3GetMemoryPage",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(cnp_class.enum_type),    # < e_RamMode *mode
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

        self.Asap3GetModuleSecJobName = self._map_symbol(
            func_name="Asap3GetModuleSecJobName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char* jobName
                ctypes.POINTER(wintypes.DWORD),         # < DWORD* sizeofBuffer
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetNetworkDevices = self._map_symbol(
            func_name="Asap3GetNetworkDevices",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *Name
                ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl * ModuleArray
                ctypes.POINTER(ctypes.c_uint),          # < unsigned int *count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetNetworkName = self._map_symbol(
            func_name="Asap3GetNetworkName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char *Name
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
                ctypes.POINTER(cnp_class.TTime),        # < ::TTime * timeStamp
                ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),  # < double ** values
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetNextSampleBlock = self._map_symbol(
            func_name="Asap3GetNextSampleBlock",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl _module
                ctypes.c_ushort,                        # > unsigned short taskId
                ctypes.c_long,                          # > long count_of_Samples
                ctypes.POINTER(ctypes.POINTER(cnp_class.TSampleBlockObject)),  # < tSampleBlockObject ** values
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
                ctypes.POINTER(ctypes.c_char_p),        # < char** name
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
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetParameterInfoByIndex = self._map_symbol(
            func_name="Asap3GetParameterInfoByIndex",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_uint,                          # > unsigned int index
                ctypes.POINTER(cnp_class.enum_type),    # < eTParameterClass*type
                ctypes.POINTER(cnp_class.enum_type),    # < eTSettingsParameterType* settingstype
                ctypes.POINTER(ctypes.c_ushort),        # < unsigned short* maxsize
                ctypes.POINTER(ctypes.c_char_p),        # < char** name
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

        self.Asap3GetRecorderByName = self._map_symbol(
            func_name="Asap3GetRecorderByName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char * recordername
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

        self.Asap3GetRecorderDataReduction = self._map_symbol(
            func_name="Asap3GetRecorderDataReduction",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.POINTER(ctypes.c_int),           # < int *Reduction
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

        self.Asap3GetRecorderType = self._map_symbol(
            func_name="Asap3GetRecorderType",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.POINTER(cnp_class.enum_type),    # < TRecorderType *RecorderType
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetScriptResultString = self._map_symbol(
            func_name="Asap3GetScriptResultString",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
                ctypes.c_char_p,                        # < char*resultString
                ctypes.POINTER(wintypes.DWORD),         # < DWORD *sizeofBuffer
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
                ctypes.c_char_p,                        # > char *textBuffer
                ctypes.POINTER(wintypes.DWORD),         # < DWORD *sizeofbuffer
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetSecProfileCount = self._map_symbol(
            func_name="Asap3GetSecProfileCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_uint),          # < unsigned int* count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetSecProfileIdentifier = self._map_symbol(
            func_name="Asap3GetSecProfileIdentifier",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char* identifiers
                ctypes.POINTER(wintypes.DWORD),         # < DWORD* sizeofBuffer
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3GetSecProfileInfo = self._map_symbol(
            func_name="Asap3GetSecProfileInfo",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_uint,                          # > unsigned int id
                ctypes.POINTER(cnp_class.SecProfileEntry),  # < SecProfileEntry* entry
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
                ctypes.POINTER(cnp_class.enum_type),    # < eTParameterClass* type
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
                cnp_class.enum_type,                    # > eTParameterClass type
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

        self.Asap3Init = self._map_symbol(
            func_name="Asap3Init",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.TAsap3Hdl),    # < TAsap3Hdl * hdl
                ctypes.c_ulong,                         # > unsigned long responseTimeout
                ctypes.c_char_p,                        # > const char *workingDir
                ctypes.c_ulong,                         # > unsigned long fifoSize
                ctypes.c_bool,                          # > bool debugMode
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3Init2 = self._map_symbol(
            func_name="Asap3Init2",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.TAsap3Hdl),    # < TAsap3Hdl * hdl
                ctypes.c_ulong,                         # > unsigned long responseTimeout
                ctypes.c_char_p,                        # > const char *workingDir
                ctypes.c_ulong,                         # > unsigned long fifoSize
                ctypes.c_ulong,                         # > unsigned long sampleSize
                ctypes.c_bool,                          # > bool debugMode
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3Init3 = self._map_symbol(
            func_name="Asap3Init3",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.TAsap3Hdl),    # < TAsap3Hdl * hdl
                ctypes.c_ulong,                         # > unsigned long responseTimeout
                ctypes.c_char_p,                        # > const char *workingDir
                ctypes.c_ulong,                         # > unsigned long fifoSize
                ctypes.c_ulong,                         # > unsigned long sampleSize
                ctypes.c_bool,                          # > bool debugMode
                ctypes.c_bool,                          # > bool clearDeviceList
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3Init4 = self._map_symbol(
            func_name="Asap3Init4",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.TAsap3Hdl),    # < TAsap3Hdl * hdl
                ctypes.c_ulong,                         # > unsigned long responseTimeout
                ctypes.c_char_p,                        # > const char *workingDir
                ctypes.c_ulong,                         # > unsigned long fifoSize
                ctypes.c_ulong,                         # > unsigned long sampleSize
                ctypes.c_bool,                          # > bool debugMode
                ctypes.c_bool,                          # > bool clearDeviceList
                ctypes.c_bool,                          # > bool bHexmode
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3Init5 = self._map_symbol(
            func_name="Asap3Init5",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.TAsap3Hdl),    # < TAsap3Hdl * hdl
                ctypes.c_ulong,                         # > unsigned long responseTimeout
                ctypes.c_char_p,                        # > const char *workingDir
                ctypes.c_ulong,                         # > unsigned long fifoSize
                ctypes.c_ulong,                         # > unsigned long sampleSize
                ctypes.c_bool,                          # > bool debugMode
                ctypes.c_bool,                          # > bool clearDeviceList
                ctypes.c_bool,                          # > bool bHexmode
                ctypes.c_bool,                          # > bool bModalMode
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3Init6 = self._map_symbol(
            func_name="Asap3Init6",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(cnp_class.TAsap3Hdl),    # < TAsap3Hdl *hdl
                ctypes.c_ulong,                         # > unsigned long responseTimeout
                ctypes.c_char_p,                        # > const char *projectFile
                ctypes.c_ulong,                         # > unsigned long fifoSize
                ctypes.c_ulong,                         # > unsigned long sampleSize
                ctypes.c_bool,                          # > bool debugMode
                ctypes.c_bool,                          # > bool clearDeviceList
                ctypes.c_bool,                          # > bool bHexmode
                ctypes.c_bool,                          # > bool bModalMode
                ctypes.POINTER(cnp_class.TApplicationID),  # < TApplicationID  *strApplication
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

        self.Asap3IsNANUsed = self._map_symbol(
            func_name="Asap3IsNANUsed",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_bool),          # < bool *use
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

        self.Asap3IsRecorderBusLoggingEnableByModule = self._map_symbol(
            func_name="Asap3IsRecorderBusLoggingEnableByModule",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(wintypes.BOOL),          # < BOOL *enable
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsRecorderBusLoggingEnableByNetWork = self._map_symbol(
            func_name="Asap3IsRecorderBusLoggingEnableByNetWork",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_char_p,                        # > char* NetworkName
                ctypes.POINTER(wintypes.BOOL),          # < BOOL *enable
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

        self.Asap3IsRestartMeasurementOnErrorEnabled = self._map_symbol(
            func_name="Asap3IsRestartMeasurementOnErrorEnabled",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_bool),          # < bool *restart
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsResumeModeActive = self._map_symbol(
            func_name="Asap3IsResumeModeActive",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_bool),          # < bool *enabled
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsTimeSyncEnabled = self._map_symbol(
            func_name="Asap3IsTimeSyncEnabled",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_bool),          # < bool *enabled
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3IsUsCANapeVersion = self._map_symbol(
            func_name="Asap3IsUsCANapeVersion",
            restype=ctypes.c_bool,
            argtypes=[
                ctypes.POINTER(wintypes.BOOL),          # < BOOL *USVersion
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

        self.Asap3MDFConvert = self._map_symbol(
            func_name="Asap3MDFConvert",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *converterID
                ctypes.c_char_p,                        # > const char *mdfFilename
                ctypes.c_char_p,                        # > const char *destFilename
                ctypes.c_bool,                          # > bool overwrite
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3MDFConverterCount = self._map_symbol(
            func_name="Asap3MDFConverterCount",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.POINTER(ctypes.c_int),           # < int *count
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3MDFConverterInfo = self._map_symbol(
            func_name="Asap3MDFConverterInfo",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_int,                           # > int index
                ctypes.POINTER(cnp_class.TConverterInfo),  # < TConverterInfo* item
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3MatlabConversion = self._map_symbol(
            func_name="Asap3MatlabConversion",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *mdfFilename
                ctypes.c_char_p,                        # > const char *matlabFilename
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3MatlabConversionAsync = self._map_symbol(
            func_name="Asap3MatlabConversionAsync",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *mdfFilename
                ctypes.c_char_p,                        # > const char *matlabFilename
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

        self.Asap3OpenDisplay = self._map_symbol(
            func_name="Asap3OpenDisplay",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *Title
                ctypes.c_int,                           # > int         Editable
                ctypes.c_int,                           # > int         Graphical
                ctypes.c_int,                           # > int         CountParameterLabelsList
                ctypes.POINTER(ctypes.c_char_p),        # < const char *ParameterLabelList[]
                ctypes.c_char_p,                        # > const char *DataDescFile
                ctypes.c_char_p,                        # > const char *DataVersFile
                ctypes.c_int,                           # > int         CountAppHistList
                ctypes.POINTER(ctypes.c_char_p),        # < const char *AppHistLabelList[]
                ctypes.POINTER(ctypes.c_char_p),        # < const char *AppHistTextList[]
                ctypes.c_char_p,                        # > const char *AppHistDefault
                ctypes.POINTER(ctypes.c_int),           # < int        *CountModified
                ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)),  # < const char **ModifiedLabelList[]
                ctypes.POINTER(ctypes.c_int),           # < int         *CountErrors
                ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)),  # < const char **ErrorLabelList[]
                ctypes.POINTER(ctypes.c_int),           # < int         *CountModAppList
                ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)),  # < const char **ModAppHistLabelList[]
                ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)),  # < const char **ModAppHistTextList[]
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3OpenDisplayForFile = self._map_symbol(
            func_name="Asap3OpenDisplayForFile",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *Patternfile
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
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ReadByAddress = self._map_symbol(
            func_name="Asap3ReadByAddress",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_ulong,                         # > unsigned long addr
                ctypes.c_ubyte,                         # > unsigned char addrExt
                ctypes.c_ulong,                         # > unsigned long size
                ctypes.POINTER(ctypes.c_ubyte),         # < unsigned char * data
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3ReadCalibrationObject = self._map_symbol(
            func_name="Asap3ReadCalibrationObject",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.POINTER(cnp_class.TCalibrationObjectValue),  # < TCalibrationObjectValue * value
            ],
            errcheck=self._get_last_error,
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

        self.Asap3ReadCalibrationObjectEx = self._map_symbol(
            func_name="Asap3ReadCalibrationObjectEx",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.POINTER(cnp_class.TCalibrationObjectValueEx),  # < TCalibrationObjectValueEx * value
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

        self.Asap3ReleaseResultList = self._map_symbol(
            func_name="Asap3ReleaseResultList",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_int,                           # > const int CountResults
                ctypes.POINTER(ctypes.c_char_p),        # < const char *ResultList[]
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

        self.Asap3RemoveItemFromRecorder = self._map_symbol(
            func_name="Asap3RemoveItemFromRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const  char* MeasurementObject
                cnp_class.TRecorderID,                  # > TRecorderID RecorderID
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3RemoveRecorder = self._map_symbol(
            func_name="Asap3RemoveRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
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

        self.Asap3RestartMeasurementOnError = self._map_symbol(
            func_name="Asap3RestartMeasurementOnError",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_bool,                          # > bool restart
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3RestoreWndSize = self._map_symbol(
            func_name="Asap3RestoreWndSize",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3RestoreWndSize2 = self._map_symbol(
            func_name="Asap3RestoreWndSize2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_long,                          # > long params
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SaveDebugWindow = self._map_symbol(
            func_name="Asap3SaveDebugWindow",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *fileName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SelectLabelList = self._map_symbol(
            func_name="Asap3SelectLabelList",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *Name
                ctypes.c_bool,                          # > bool includeMeaMode = true
                cnp_class.enum_type,                    # > enLabelListMode mode = e_AddSignals
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SelectModuleLabelList = self._map_symbol(
            func_name="Asap3SelectModuleLabelList",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char* Name
                ctypes.c_bool,                          # > bool includeMeaMode = true
                cnp_class.enum_type,                    # > enLabelListMode mode = e_AddSignals
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SelectObjects = self._map_symbol(
            func_name="Asap3SelectObjects",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                cnp_class.enum_type,                    # > TObjectType type
                ctypes.c_char_p,                        # > const char *fname
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SelectRecorder = self._map_symbol(
            func_name="Asap3SelectRecorder",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetApplicationName = self._map_symbol(
            func_name="Asap3SetApplicationName",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *AppName
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetCanapeModuleParam = self._map_symbol(
            func_name="Asap3SetCanapeModuleParam",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > char* param
                ctypes.c_char_p,                        # > char *value
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetCanapeProjectParam = self._map_symbol(
            func_name="Asap3SetCanapeProjectParam",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *Section
                ctypes.c_char_p,                        # > char *param
                ctypes.c_char_p,                        # > char* value
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

        self.Asap3SetMdfFilename = self._map_symbol(
            func_name="Asap3SetMdfFilename",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char *mdfFilename
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetMeasurementComment = self._map_symbol(
            func_name="Asap3SetMeasurementComment",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > const char* comment
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetRecorderDataReduction = self._map_symbol(
            func_name="Asap3SetRecorderDataReduction",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TRecorderID,                  # > TRecorderID recorderID
                ctypes.c_int,                           # > int Reduction
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

        self.Asap3SetResumeMode = self._map_symbol(
            func_name="Asap3SetResumeMode",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
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

        self.Asap3SetupDataAcquisitionChnl = self._map_symbol(
            func_name="Asap3SetupDataAcquisitionChnl",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *measurementObjectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.c_ushort,                        # > unsigned short taskId
                ctypes.c_ushort,                        # > unsigned short pollingRate
                ctypes.c_bool,                          # > bool save2File
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetupDataAcquisitionChnl2 = self._map_symbol(
            func_name="Asap3SetupDataAcquisitionChnl2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *measurementObjectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.c_ushort,                        # > unsigned short taskId
                ctypes.c_ushort,                        # > unsigned short pollingRate
                ctypes.c_bool,                          # > bool save2File
                ctypes.c_bool,                          # > bool transfer_To_Client
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SetupFifo = self._map_symbol(
            func_name="Asap3SetupFifo",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_ushort,                        # > unsigned short nFifoSize
                ctypes.POINTER(cnp_class.TFifoSize),    # < tFifoSize fifoSize[]
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

        self.Asap3StartDataAcquisition2 = self._map_symbol(
            func_name="Asap3StartDataAcquisition2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_uint,                          # > unsigned int errtimeout = 0
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StartDataAcquisition3 = self._map_symbol(
            func_name="Asap3StartDataAcquisition3",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_uint,                          # > unsigned int timeout
                ctypes.c_bool,                          # > bool StartwithoutRecording = false
                ctypes.c_bool,                          # > bool resumemode=false
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

        self.Asap3StartResumedDataAcquisition = self._map_symbol(
            func_name="Asap3StartResumedDataAcquisition",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StartResumedDataAcquisition2 = self._map_symbol(
            func_name="Asap3StartResumedDataAcquisition2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_uint,                          # > unsigned int timeout
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3StartScript = self._map_symbol(
            func_name="Asap3StartScript",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
                ctypes.c_char_p,                        # > char *Commandline = NULL
                cnp_class.TModulHdl,                    # > TModulHdl moduleHdl=ASAP3_INVALID_MODULE_HDL
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

        self.Asap3StopDataAcquisition2 = self._map_symbol(
            func_name="Asap3StopDataAcquisition2",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_ulong,                         # > unsigned long timeout = NULL
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

        self.Asap3StopScript = self._map_symbol(
            func_name="Asap3StopScript",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TScriptHdl,                   # > TScriptHdl hScript
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3SwitchToMemoryPage = self._map_symbol(
            func_name="Asap3SwitchToMemoryPage",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                cnp_class.enum_type,                    # > e_RamMode mode
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

        self.Asap3TimeSync = self._map_symbol(
            func_name="Asap3TimeSync",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_bool,                          # > bool enabled
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3TransmitFile2ClientPc = self._map_symbol(
            func_name="Asap3TransmitFile2ClientPc",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_char_p,                        # > char *srcFname
                ctypes.c_char_p,                        # > char *dstFname
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3UnRegisterCallBack = self._map_symbol(
            func_name="Asap3UnRegisterCallBack",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.enum_type,                    # > ASAP3_EVENT_CODE eventID
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3UseNAN = self._map_symbol(
            func_name="Asap3UseNAN",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                ctypes.c_bool,                          # > bool use
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3WriteByAddress = self._map_symbol(
            func_name="Asap3WriteByAddress",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_ulong,                         # > unsigned long addr
                ctypes.c_ubyte,                         # > unsigned char addrExt
                ctypes.c_ulong,                         # > unsigned long size
                ctypes.POINTER(ctypes.c_ubyte),         # < unsigned char * data
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
                ctypes.POINTER(cnp_class.TCalibrationObjectValue),  # < TCalibrationObjectValue * value
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3WriteCalibrationObjectEx = self._map_symbol(
            func_name="Asap3WriteCalibrationObjectEx",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.c_char_p,                        # > const char *calibrationObjectName
                cnp_class.enum_type,                    # > TFormat format
                ctypes.POINTER(cnp_class.TCalibrationObjectValueEx),  # < TCalibrationObjectValueEx * value
            ],
            errcheck=self._get_last_error,
        )

        self.Asap3_CCP_Request = self._map_symbol(
            func_name="Asap3_CCP_Request",
            restype=ctypes.c_bool,
            argtypes=[
                cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
                cnp_class.TModulHdl,                    # > TModulHdl module
                ctypes.POINTER(ctypes.c_ubyte),         # < const unsigned char *requestData
                ctypes.c_ulong,                         # > unsigned long  requestSize
                ctypes.c_ulong,                         # > unsigned long  responseTimeout
                ctypes.POINTER(ctypes.c_ubyte),         # < unsigned char * responseData
                ctypes.c_ulong,                         # > unsigned long  maxResponseSize
                ctypes.POINTER(ctypes.c_ulong),         # < unsigned long * responseSize
            ],
            errcheck=self._get_last_error,
        )

    # fmt: on

    @functools.cached_property
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
            error_msg = f"{cnp_constants.ErrorCodes(error_code).name}: {ptr.contents.value.decode('ascii')}"  # type: ignore[union-attr]
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
                f"Function '{func_name}' not found in "
                f"{Path(self.windll._name).name} (v{self.version})"
            )
            LOG.debug(warning_msg)
            # the function is not available, replace it with another function, that will raise a `NotImplementedError`
            symbol = functools.partial(self._not_implemented, func_name, self.version)
        else:
            symbol.__name__ = func_name

            if errcheck:
                symbol.errcheck = errcheck

        func = _synchronize(symbol)
        return func

    @staticmethod
    def _not_implemented(
        func_name: str, dll_version: Version, *_args: Any, **_kwargs: Any
    ) -> None:
        err_msg = f"The function '{func_name}' was not found in CANape DLL version {dll_version}."
        raise NotImplementedError(err_msg)
