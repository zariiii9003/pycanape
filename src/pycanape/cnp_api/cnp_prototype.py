import ctypes
from ctypes import wintypes
import platform

from . import cnp_class, cnp_constants
from ..utils import CLibrary, CANapeError

DLL_NAME = "CANapAPI64" if platform.architecture()[0] == "64bit" else "CANapAPI"
CANAPEAPI = CLibrary(DLL_NAME)


def get_last_error(result, function, arguments):
    if result:
        return

    error_code = Asap3GetLastError(arguments[0])
    buffer = ctypes.c_char_p()
    ptr = ctypes.pointer(buffer)

    Asap3ErrorText(
        arguments[0],
        error_code,
        ptr,
    )

    if error_code > 0:
        error_msg = (
            f"{cnp_constants.ErrorCodes(error_code).name}: "
            f"{ptr.contents.value.decode('ascii')}"
        )
        raise CANapeError(error_code, error_msg, function.__name__)


# fmt: off
Asap3CalibrationObjectInfoEx = CANAPEAPI.map_symbol(
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
    errcheck=get_last_error,
)

Asap3CheckOverrun = CANAPEAPI.map_symbol(
    func_name="Asap3CheckOverrun",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.c_ushort,                        # > unsigned short taskId
        ctypes.c_bool,                          # > bool resetOverrun
    ],
    errcheck=get_last_error,
)

Asap3CreateModule = CANAPEAPI.map_symbol(
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
    errcheck=get_last_error,
)

Asap3CreateModule3 = CANAPEAPI.map_symbol(
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
    errcheck=get_last_error,
)

Asap3DefineRecorder = CANAPEAPI.map_symbol(
    func_name="Asap3DefineRecorder",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.c_char_p,                        # > char *RecorderName
        ctypes.POINTER(cnp_class.TRecorderID),  # < TRecorderID * trecorder
        cnp_class.enum_type,                    # > TRecorderType RecorderType=eTRecorderTypeMDF
    ],
    errcheck=get_last_error,
)

Asap3ECUOnOffline = CANAPEAPI.map_symbol(
    func_name="Asap3ECUOnOffline",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        cnp_class.enum_type,                    # > TAsap3ECUState State
        ctypes.c_bool,                          # > bool download
    ],
    errcheck=get_last_error,
)

Asap3EnableRecorder = CANAPEAPI.map_symbol(
    func_name="Asap3EnableRecorder",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
        ctypes.c_bool,                          # > bool enable
    ],
    errcheck=get_last_error,
)

Asap3ErrorText = CANAPEAPI.map_symbol(
    func_name="Asap3ErrorText",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.c_ushort,                        # > unsigned short errCode
        ctypes.POINTER(ctypes.c_char_p),        # < char ** errMsg
    ],
)

Asap3Exit2 = CANAPEAPI.map_symbol(
    func_name="Asap3Exit2",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.c_bool,                          # > bool close_CANape
    ],
    errcheck=get_last_error,
)

Asap3GetApplicationVersion = CANAPEAPI.map_symbol(
    func_name="Asap3GetApplicationVersion",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.POINTER(cnp_class.Appversion),   # < Appversion * version
    ],
    errcheck=get_last_error,
)

Asap3GetCommunicationType = CANAPEAPI.map_symbol(
    func_name="Asap3GetCommunicationType",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(ctypes.c_char_p),        # < char ** commType
    ],
    errcheck=get_last_error,
)

Asap3GetCurrentValues = CANAPEAPI.map_symbol(
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
    errcheck=get_last_error,
)

Asap3GetDBObjectInfo = CANAPEAPI.map_symbol(
    func_name="Asap3GetDBObjectInfo",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.c_char_p,                        # > char *ObjectName
        ctypes.POINTER(cnp_class.DBObjectInfo),  # < DBObjectInfo *Info
    ],
    errcheck=get_last_error,
)

Asap3GetEcuDriverType = CANAPEAPI.map_symbol(
    func_name="Asap3GetEcuDriverType",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(cnp_class.enum_type),    # < tDriverType *DriverType
    ],
    errcheck=get_last_error,
)

Asap3GetEcuTasks = CANAPEAPI.map_symbol(
    func_name="Asap3GetEcuTasks2",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(cnp_class.TTaskInfo),    # < TTaskInfo * taskInfo
        ctypes.POINTER(ctypes.c_ushort),        # < unsigned short *noTasks
        ctypes.c_short,                         # > unsigned short maxTaskInfo
    ]
)

Asap3GetEcuTasks2 = CANAPEAPI.map_symbol(
    func_name="Asap3GetEcuTasks2",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(cnp_class.TTaskInfo2),   # < TTaskInfo2 * taskInfo2
        ctypes.POINTER(ctypes.c_ushort),        # < unsigned short *noTasks
        ctypes.c_short,                         # > unsigned short maxTaskInfo
    ],
    errcheck=get_last_error,
)

Asap3GetFifoLevel = CANAPEAPI.map_symbol(
    func_name="Asap3GetFifoLevel",
    restype=ctypes.c_long,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.c_ushort,                        # > unsigned short taskId
    ],
)

Asap3GetLastError = CANAPEAPI.map_symbol(
    func_name="Asap3GetLastError",
    restype=ctypes.c_ushort,
    argtypes=[cnp_class.TAsap3Hdl],             # > TAsap3Hdl hdl
)

Asap3GetMeasurementListEntries = CANAPEAPI.map_symbol(
    func_name="Asap3GetMeasurementListEntries",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(ctypes.POINTER(cnp_class.MeasurementListEntries)),  # < MeasurementListEntries **Items
    ],
    errcheck=get_last_error,
)

Asap3GetMeasurementState = CANAPEAPI.map_symbol(
    func_name="Asap3GetMeasurementState",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.POINTER(cnp_class.enum_type),    # > tMeasurementState *State
    ],
    errcheck=get_last_error,
)

Asap3GetModuleCount = CANAPEAPI.map_symbol(
    func_name="Asap3GetModuleCount",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *count
    ],
    errcheck=get_last_error,
)

Asap3GetModuleHandle = CANAPEAPI.map_symbol(
    func_name="Asap3GetModuleHandle",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.c_char_p,                        # > const char *moduleName
        ctypes.POINTER(cnp_class.TModulHdl),    # < TModulHdl * module
    ],
    errcheck=get_last_error,
)

Asap3GetModuleName = CANAPEAPI.map_symbol(
    func_name="Asap3GetModuleName",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(ctypes.c_char_p),        # < char **moduleName
    ],
    errcheck=get_last_error,
)

Asap3GetNetworkName = CANAPEAPI.map_symbol(
    func_name="Asap3GetNetworkName",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.c_char_p,                        # < char *Name
        ctypes.POINTER(ctypes.c_uint),          # < unsigned int * sizeofName
    ],
    errcheck=get_last_error,
)

Asap3GetNextSample = CANAPEAPI.map_symbol(
    func_name="Asap3GetNextSample",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.c_ushort,                        # > unsigned short taskId
        ctypes.POINTER(cnp_class.TTime),        # < TTime * timeStamp
        ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),  # < double ** values
    ],
    errcheck=get_last_error,
)

Asap3GetProjectDirectory = CANAPEAPI.map_symbol(
    func_name="Asap3GetProjectDirectory",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.c_char_p,                        # < char* directory
        ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *size
    ],
    errcheck=get_last_error,
)

Asap3GetRecorderByIndex = CANAPEAPI.map_symbol(
    func_name="Asap3GetRecorderByIndex",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.c_ulong,                         # > unsigned long index
        ctypes.POINTER(cnp_class.TRecorderID),  # < TRecorderID *recorderID
    ],
    errcheck=get_last_error,
)

Asap3GetRecorderCount = CANAPEAPI.map_symbol(
    func_name="Asap3GetRecorderCount",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.POINTER(ctypes.c_ulong),         # < unsigned long *count
    ],
    errcheck=get_last_error,
)

Asap3GetRecorderMdfFileName = CANAPEAPI.map_symbol(
    func_name="Asap3GetRecorderMdfFileName",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
        ctypes.c_char_p,                        # < char *FileName
        ctypes.POINTER(wintypes.DWORD),         # < DWORD *size
    ],
    errcheck=get_last_error,
)

Asap3GetRecorderName = CANAPEAPI.map_symbol(
    func_name="Asap3GetRecorderName",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
        ctypes.c_char_p,                        # < char * recorderName
        ctypes.POINTER(ctypes.c_long),          # < long *Size
    ],
    errcheck=get_last_error,
)

Asap3GetRecorderState = CANAPEAPI.map_symbol(
    func_name="Asap3GetRecorderState",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
        ctypes.POINTER(cnp_class.enum_type),    # < EnRecorderState *State
    ],
    errcheck=get_last_error,
)

Asap3GetSelectedRecorder = CANAPEAPI.map_symbol(
    func_name="Asap3GetSelectedRecorder",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.POINTER(cnp_class.TRecorderID),  # < TRecorderID *recorderID
    ],
    errcheck=get_last_error,
)

Asap3HasMCD3License = CANAPEAPI.map_symbol(
    func_name="Asap3HasMCD3License",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.POINTER(ctypes.c_bool),          # < bool *available
    ],
    errcheck=get_last_error,
)

Asap3HasResumeMode = CANAPEAPI.map_symbol(
    func_name="Asap3HasResumeMode",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(ctypes.c_bool),          # < bool *possible
    ],
    errcheck=get_last_error,
)

Asap3Init5 = CANAPEAPI.map_symbol(
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
)

Asap3IsECUOnline = CANAPEAPI.map_symbol(
    func_name="Asap3IsECUOnline",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(cnp_class.enum_type),    # < TAsap3ECUState *State
    ],
    errcheck=get_last_error,
)

Asap3IsModuleActive = CANAPEAPI.map_symbol(
    func_name="Asap3IsModuleActive",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.POINTER(ctypes.c_bool),          # < bool *activate
    ],
    errcheck=get_last_error,
)

Asap3IsNetworkActivated = CANAPEAPI.map_symbol(
    func_name="Asap3IsNetworkActivated",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.c_char_p,                        # > char *Name
        ctypes.POINTER(ctypes.c_bool),          # < bool *activated
    ],
    errcheck=get_last_error,
)

Asap3IsRecorderEnabled = CANAPEAPI.map_symbol(
    func_name="Asap3IsRecorderEnabled",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
        ctypes.POINTER(ctypes.c_bool),          # < bool *enabled
    ],
    errcheck=get_last_error,
)

Asap3ModuleActivation = CANAPEAPI.map_symbol(
    func_name="Asap3ModuleActivation",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.c_bool,                          # > bool activate
    ],
    errcheck=get_last_error,
)

Asap3PauseRecorder = CANAPEAPI.map_symbol(
    func_name="Asap3PauseRecorder",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
        ctypes.c_bool,                          # > bool Pause
    ],
    errcheck=get_last_error,
)

Asap3PopupDebugWindow = CANAPEAPI.map_symbol(
    func_name="Asap3PopupDebugWindow",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
    ]
)

Asap3ReadCalibrationObject2 = CANAPEAPI.map_symbol(
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
    errcheck=get_last_error,
)

Asap3ReadObjectParameter = CANAPEAPI.map_symbol(
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
    errcheck=get_last_error,
)

Asap3ReleaseModule = CANAPEAPI.map_symbol(
    func_name="Asap3ReleaseModule",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
    ],
    errcheck=get_last_error,
)

Asap3ResetDataAcquisitionChnls = CANAPEAPI.map_symbol(
    func_name="Asap3ResetDataAcquisitionChnls",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
    ],
    errcheck=get_last_error,
)

Asap3ResetDataAcquisitionChnlsByModule = CANAPEAPI.map_symbol(
    func_name="Asap3ResetDataAcquisitionChnlsByModule",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl hmod
    ],
    errcheck=get_last_error,
)

Asap3SetInteractiveMode = CANAPEAPI.map_symbol(
    func_name="Asap3SetInteractiveMode",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        ctypes.c_bool,                          # > bool mode
    ],
    errcheck=get_last_error,
)

Asap3SetRecorderMdfFileName = CANAPEAPI.map_symbol(
    func_name="Asap3SetRecorderMdfFileName",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
        ctypes.c_char_p,                        # > char *FileName
    ],
    errcheck=get_last_error,
)

Asap3SetTCPOptions = CANAPEAPI.map_symbol(
    func_name="Asap3SetTCPOptions",
    restype=ctypes.c_bool,
    argtypes=[
        ctypes.c_char_p,                        # > const char* ipAddress
        ctypes.c_ulong,                         # > unsigned long portNumber
    ],
)

Asap3SetupDataAcquisitionChnl = CANAPEAPI.map_symbol(
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
    errcheck=get_last_error,
)

Asap3StartDataAcquisition = CANAPEAPI.map_symbol(
    func_name="Asap3StartDataAcquisition",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
    ],
    errcheck=get_last_error,
)

Asap3StartRecorder = CANAPEAPI.map_symbol(
    func_name="Asap3StartRecorder",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
    ],
    errcheck=get_last_error,
)

Asap3StopRecorder = CANAPEAPI.map_symbol(
    func_name="Asap3StopRecorder",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TRecorderID,                  # > TRecorderID recorderID
        ctypes.c_bool,                          # > bool save2Mdf
    ],
    errcheck=get_last_error,
)

Asap3StopDataAcquisition = CANAPEAPI.map_symbol(
    func_name="Asap3StopDataAcquisition",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
    ],
    errcheck=get_last_error,
)

Asap3TestObject = CANAPEAPI.map_symbol(
    func_name="Asap3TestObject",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.c_char_p,                        # > const char * objectName
        ctypes.POINTER(cnp_class.enum_type),    # < TObjectType * type
    ],
    errcheck=get_last_error,
)

Asap3WriteCalibrationObject = CANAPEAPI.map_symbol(
    func_name="Asap3WriteCalibrationObject",
    restype=ctypes.c_bool,
    argtypes=[
        cnp_class.TAsap3Hdl,                    # > TAsap3Hdl hdl
        cnp_class.TModulHdl,                    # > TModulHdl module
        ctypes.c_char_p,                        # > const char *calibrationObjectName
        cnp_class.enum_type,                    # > TFormat format
        ctypes.POINTER(cnp_class.TCalibrationObjectValue),  # > TCalibrationObjectValue * value
    ],
    errcheck=get_last_error,
)
