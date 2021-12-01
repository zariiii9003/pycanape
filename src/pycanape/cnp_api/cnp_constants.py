from enum import IntEnum

CANAPE_API_MAIN_VESION = 2
CANAPE_API_SUB_VESION = 3
CANAPE_API_RELEASE = 1
CANAPE_API_OS_VERSION = "Windows95/WindowsNT"
CANAPE_API_OS_RELEASE = 1
MAX_OS_VERSION = 50

ASAP3_INVALID_MODULE_HDL = -1

# Definitions used by function Asap3GetDatabaseObjectsByType
TDBE_VALUE_SCALAR = 0x00000001  # definition for scalar object selection
TDBE_VALUE_CURVE = 0x00000002  # definition for curve object selection
TDBE_VALUE_MAP = 0x00000004  # definition for map object selection
TDBE_VALUE_AXIS = 0x00000008  # definition for axis object selection
TDBE_VALUE_ASCII = 0x00000010  # definition for ASCII object selection
TDBE_VALUE_VALBLK = 0x00000020  # definition for Value Block object selection
TDBE_VALUE_TEMPLATE = 0x00000040  # definition for Includeing templates
TDBE_VALUE_ALL = (
    TDBE_VALUE_SCALAR
    | TDBE_VALUE_CURVE
    | TDBE_VALUE_MAP
    | TDBE_VALUE_AXIS
    | TDBE_VALUE_ASCII
    | TDBE_VALUE_VALBLK
)  # definition for all object types without templates
TDBE_VALUE_INCLUDING_TEMPLATES = (
    TDBE_VALUE_SCALAR
    | TDBE_VALUE_CURVE
    | TDBE_VALUE_MAP
    | TDBE_VALUE_AXIS
    | TDBE_VALUE_ASCII
    | TDBE_VALUE_VALBLK
    | TDBE_VALUE_TEMPLATE
)  # definition for all object types including templates


class ErrorCodes(IntEnum):
    AEC_CMD_NOT_SUP = 1  # Command not supported
    AEC_INTERFACE_NOTSUPPORTED = 2  # Interface type not supported
    AEC_CREATE_MEM_MAPPED_FILE = 3  # Error creating memory mapped file
    AEC_WRITE_CMD = 4  # Error writing data to memory mapped file
    AEC_READ_RESPONSE = 5  # Error reading response from memory mapped file
    AEC_ASAP2_FILE_NOT_FOUND = 6  # ASAP2 file not found
    AEC_INVALID_MODULE_HDL = 7  # Invalid module handle
    AEC_ERR_OPEN_FILE = 8  # Open file error
    AEC_UNKNOWN_OBJECT = 9  # Unknown object name
    AEC_NO_DATABASE = 10  # No database assigned
    AEC_PAR_SIZE_OVERFLOW = 11  # Parameter 'size' too large
    AEC_NOT_WRITE_ACCESS = 12  # Object has no write access
    AEC_OBJECT_TYPE_DOESNT_MATCH = 13  # Object type doens't match
    AEC_NO_TASKS_OVERFLOW = 14  # Number of tasks overflow
    AEC_CCP_RESPONSE_SIZE_INVALID = 15  # Invalid CCP response size
    AEC_TIMEOUT_RESPONSE = 16  # Timeout reading response from memory mapped file
    AEC_NO_VALUES_SAMPLED = 17  # FIFO doesn't contain any values
    AEC_ACQ_CHNL_OVERRUN = 18  # Too many channels defined relating to single raster
    AEC_NO_RASTER_OVERFLOW = 19  # Too many rasters selected for data acquisition (overflow of internal parameter)
    AEC_CANAPE_CREATE_PROC_FAILED = 20  # CreateProcess of CANape failed
    AEC_EXIT_DENIED_WHILE_ACQU = (
        21  # Asap3Exit denied because data acquistion is still running
    )
    AEC_WRITE_DATA_FAILED = 22  # Error writing data to application RAM
    AEC_NO_RESPONSE_FROM_ECU = 23  # No response from ECU (attach Asap2 failed)
    AEC_ACQUIS_ALREADY_RUNNING = (
        24  # Asap3StartDataAcquisition denied: data acquisition already running
    )
    AEC_ACQUIS_NOT_STARTED = (
        25  # Asap3StopAcquisition denied: data acquisition not started
    )
    AEC_VALUES_NOT_ACCESSIBLE = 26  # If cache is disabled, values aren't accessible while acquisition is running
    AEC_NO_AXIS_PTS_NOT_VALID = (
        27  # Invalid number of axis points (see following note).
    )
    AEC_SCRIPT_CMD_TO_LARGE = 28  # Script command size overflow
    AEC_SCRIPT_CMD_INVALID = 29  # Invalid/unknown script command
    AEC_UNKNOWN_MODULE_NAME = 30  # Unknown module
    AEC_FIFO_INTERNAL_ERROR = 31  # CANape internal error concerning FIFO management
    AEC_VERSION_ERROR = 32  # Access denied: incompatible CANape version
    AEC_ILLEGAL_DRIVER = 33  # Illegal driver type
    AEC_CALOBJ_READ_FAILED = 34  # Read of calibration object failed
    AEC_ACQ_STP_INIT_FAILED = 35  # Initialization of data acquisition failed
    AEC_ACQ_STP_PROC_FAILED = 36  # Data acquisition failed
    AEC_ACQ_STP_OVERFLOW = 37  # Buffer overflow at data acquisition
    AEC_ACQ_STP_TIME_OVER = (
        38  # Data acquisition stopped because selected time is elapsed
    )
    AEC_NOSERVER_ERRCODE = 40  # No Server application available
    AEC_ERR_OPEN_DATADESCFILE = (
        41  # Unable to open data description file, may be nonexistent
    )
    AEC_ERR_OPEN_DATAVERSFILE = 42  # Unable to open a data file
    AEC_TO_MUCH_DISPLAYS_OPEN = 43  # Maximal count of displays are opened
    AEC_INTERNAL_CANAPE_ERROR = 44  # Attempt to create a module failed
    AEC_CANT_OPEN_DISPLAY = 45  # Unable to open a display
    AEC_ERR_NO_PATTERNFILE_DEFINED = 46  # No parameter filename
    AEC_ERR_OPEN_PATTERNFILE = 47  # Unable to open patternfile
    AEC_ERR_CANT_RELEASE_MUTEX = 48  # Release of a mutex failed
    AEC_WRONG_CANAPE_VERSION = 49  # Canape does not fit to dll version
    AEC_TCP_SERV_CONNECT_FAILED = 50  # Connect to ASAP3 server failed
    AEC_TCP_MISSING_CFG = 51  # Missing CANape TCP Server configuration
    AEC_TCP_SERV_NOT_CONNECTED = (
        52  # Connection between ASAP3 Server and TCP CANapeAPI is not active
    )
    AEC_TCP_EXIT_NOTCLOSED = 53  #
    AEC_FIFO_ALREADY_INIT = (
        54  # The FIFO Memory was already created. Close all conections to reconfigure.
    )
    AEC_ILLEGAL_OPERATION = 55  # It is not possible to operate this command
    AEC_WRONG_TYPE = 56  # The given type is not supported
    AEC_NO_CANAPE_LICENSE = 57  # CANape is not licensed
    AEC_REG_OPEN_KEY_FAILED = 58  # Key "HKEY_LOCAL_MACHINE\\SOFTWARE\\VECTOR\\CANape" missing at Windows Registry, maybe CANape setup has not been correctly performed
    AEC_REG_QUERY_VALUE_FAILED = 59  # Value "Path" missing at Windows Registry, maybe CANape setup has not been correctly performed
    AEC_WORKDIR_ACCESS_FAILED = (
        60  # CreateProcess of CANape failed: working directory not accessible/exists
    )
    AEC_INIT_COM_FAILED = 61  # Internal error: Asap3InitCom() failed
    AEC_INIT_CMD_FAILED = 62  # Negative Response from CANape: Init() failed
    AEC_CANAPE_INVALID_PRG_PATH = 63  # CreateProcess of CANape failed: programme directory not accessible/nonexistent
    AEC_INVALID_ASAP3_HDL = 64  # Invalid asap3 handle
    AEC_LOADING_FILE = 65  # File loading failed
    AEC_SAVING_FILE = 66  # File saving failed
    AEC_UPLOAD = 67  # Upload failed
    AEC_WRITE_VALUE_ERROR = 68  # Value could not be written
    AEC_TMTF_NOT_FINSHED = 69  # Other file transmission in process
    AEC_TMTF_SEQUENCE_ERROR = 70  # TransmitFile: sequence error (internal error)
    AEC_TDBO_TYPE_ERROR = 71  # TransmitFile: sequence error (internal error)
    AEC_EXECUTE_SERVICE_ERROR = 72  # Asap3_CCP_Request failed
    AEC_INVALID_DRIVERTYPE = 73  # Invalid drivertype for this operation
    AEC_DIAG_INVALID_DRIVERTYPE = 74  # Invalid drivertype for for diagnostic operations
    AEC_DIAG_INVALID_BUSMESSAGE = 75  # Invalid BusMessage
    AEC_DIAG_INVALID_VARIANT = 76  # Invalid Variant
    AEC_DIAG_INVALID_DIAGSERVICE = 77  # Invalid or unknown request
    AEC_DIAG_ERR_EXECUTE_SERVICE = 78  # Error while sending service
    AEC_DIAG_INVALID_PARAMS = 79  # Invalid or unknown request
    AEC_DIAG_UNKNOWN_PARAM_NAME = 80  # Invalid or unknown parameter name
    AEC_DIAG_EXCEPTION_ERROR = 81  # Error while creating a request
    AEC_DIAG_INVALID_RESPONSE = 82  # Error response cannot be handled
    AEC_DIAG_UNKNOWN_PARAM_TYPE = 83  # Unknown parameter type
    AEC_DIAG_NO_INFO_AVAILABLE = 84  # Currently no information available
    AEC_DIAG_UNKNOWN_RESPHANDLE = 85  # Unknown response handle
    ACE_DIAG_WRONG_SERVICE_STATE = (
        86  # The current request is in the wrong state for this operation
    )
    AEC_DIAG_INVALID_INDEX_SIZE = 87  # Complex index does not match
    AEC_DIAG_INVALID_RESPONSETYPE = 88  # Invalid response type
    AEC_FLASH_INVALID_MANAGER = 89  # Flash manager invalid
    AEC_FLASH_OBJ_OUT_OF_RANGE = 90  # Flash object out of range
    AEC_FLASH_MANAGER_ERROR = 91  # Flash manager error
    AEC_FLASH_ALLREADY_RUNNING = 92  #
    AEC_FLASH_INVALID_APPNAME = 93  # Invalid application name
    AEC_FUNCTION_NOT_SUPPORTED = (
        94  # This function is not supported in this program version
    )
    AEC_LICENSE_NOT_FOUND = 95  # License file not found
    AEC_RECORDER_ALLREADY_EXISTS = 96  # Recorder already exists
    AEC_RECORDER_NOT_FOUND = 97  # Recorder does not exists
    AEC_RECORDER_INDEX_OUTOFRANGE = 98  # Recorder index out of range
    AEC_REMOVE_RECORDER_ERR = 99  # Error deleting Recorder
    AEC_INVALID_PARAMETER = 100  # Wrong parameter value
    AEC_ERROR_CREATERECORDER = 101  # Error creating recorder
    AEC_ERROR_SETRECFILENAME = 102  # Error creating Filename
    AEC_ERROR_INVALID_TASKID = 103  # Invalid task id for the given Measurement object
    AEC_DIAG_PARAM_SETERROR = 104  # Parameter can not be set
    AEC_CNFG_WRONG_MODE = 105  # command not supported in current mode
    AEC_CNFG_FILE_NOT_FOUND = 106  # Specified File is Not Found
    AEC_CNFG_FILE_INVALID = 107  # File belongs to a different project
    AEC_INVALID_SCR_HANDLE = 108  # Invalid script handle
    AEC_REMOVE_SCR_HANDLE = 109  # Unable to remove Script
    AEC_ERROR_DECALRE_SCR = 110  # Unable to declare script
    AEC_ERROR_RESUME_SUPPORTED = 111  # The requested module doesn't support resume mode
    AEC_UNDEFINED_CHANNEL = 112  # undefined channel parameter
    AEC_ERR_DRIVER_CONFIG = 113  # No configuration for this drivertype available
    AEC_ERR_DCB_EXPORT = 114  # Error creating DBC export file
    ACE_NOT_AVAILABLE_WHILE_ACQ = (
        115  # Function not available while a measurement is running
    )
    ACE_NOT_MISSING_LICENSE = 116  # ILinkRT Recorder available only with option MCD3
    ACE_EVENT_ALLREADY_REGISERED = 117  # Callback Event already registered
    AEC_OBJECT_ALLREADY_DEFINED = 118  # Measurement object already defined
    AEC_CAL_NOT_ALLOWED = (
        119  # Calibration not allowed if online calibration is switched off
    )
    AEC_DIAG_UNDEFINED_JOB = 120  # Unknown service
    AEC_ERROR_MODAL_DIALOG = 121  # Prohibited command while a modal dialog is prompted
    AEC_ERROR_CHANNEL_ASSIGNMENT = 122  # hardware channel assignment"
    AEC_ERROR_STRUCTURE_OBJECT = (
        123  # Measurement object is already instantiated in a structure object
    )
    AEC_NETWORK_NOT_FOUND = 124  # Network not found or not available
    AEC_ERROR_LOADING_LABELLIST = 125  # Error loading label list
    AEC_ERROR_CONV_FILE_ACCESS = (
        126  # Currently the converter has no file access - please try it later
    )
    AEC_ERROR_COMPLEX_RESPONSES = 127  # Function not available for complex responses
    AEC_ERROR_INIPATH = 128  # Function could not determine the project directory
    AEC_USUPPORTED_INTERFACE_ID = (
        129  # Interface name is not supported with this drivertype
    )
    AEC_INSUFFICENT_BUFFERSIZE = 130  # Buffer size too small
    AEC_PATCHENTRY_NOT_FOUND = 131  # Patch section not found
    AEC_PATCHSECTION_NOT_FOUND = 132  # Patch entry not found
    AEC_SEC_MANAGER_ERROR = 133  # Security manager access error
    ACE_CHANNEL_OPTIMIZED = 134  # Measurement channel is optimized because it's parent will already be measured
    ACE_ERR_PROFILE_ID = 135  # Profile not registered
    ACE_ERR_UNSUPPORTED_TYPE = 136  # Unsupported data type for measurement
    ACE_ERR_DATA_SIZE = 137  # Datasize of object too large
    AEC_CALOBJ_INVALID_VALUE = 138  # Invalid value - object can't be read


class TApplicationType(IntEnum):
    eUNDEFINED = 0
    eCANAPE = 1
    eAPPLOCATION = 3


class Channels(IntEnum):
    # Definitions for CAN
    DEV_CAN1 = 1
    DEV_CAN2 = 2
    DEV_CAN3 = 3
    DEV_CAN4 = 4
    DEV_CAN5 = 5
    DEV_CAN6 = 6
    DEV_CAN7 = 7
    DEV_CAN8 = 8
    DEV_CAN20 = 20

    # Definitions for FlexRay 1 - 8
    DEV_FLX1 = 31
    DEV_FLX2 = 32
    DEV_FLX3 = 33
    DEV_FLX4 = 34
    DEV_FLX5 = 35
    DEV_FLX6 = 36
    DEV_FLX7 = 37
    DEV_FLX8 = 38

    # Definitions for LIN 1 - 8
    DEV_LIN1 = 61
    DEV_LIN2 = 62
    DEV_LIN3 = 63
    DEV_LIN4 = 64
    DEV_LIN5 = 65
    DEV_LIN6 = 66
    DEV_LIN7 = 67
    DEV_LIN8 = 68

    # Definitions for CAN on VX 1-4
    DEV_VX_CAN1 = 81
    DEV_VX_CAN2 = 82
    DEV_VX_CAN3 = 83
    DEV_VX_CAN4 = 84

    # Definitions for TCP on VX
    DEV_VX_TCP = 85
    DEV_VX_UDP = 86

    # Definitions for SXI
    DEV_SXI1 = 91
    DEV_SXI2 = 92
    DEV_SXI3 = 93
    DEV_SXI4 = 94
    DEV_SXI5 = 95
    DEV_SXI6 = 96
    DEV_SXI7 = 97
    DEV_SXI8 = 98

    # Definitions for USB
    DEV_USB = 110

    # Definitions for CAN CANFD
    DEV_CANFD1 = 121
    DEV_CANFD2 = 122
    DEV_CANFD3 = 123
    DEV_CANFD4 = 124
    DEV_CANFD5 = 125
    DEV_CANFD6 = 126
    DEV_CANFD7 = 127
    DEV_CANFD8 = 128
    DEV_CANFD9 = 129

    # Definitions for TCP
    DEV_TCP = 255
    # Definitions for UDP
    DEV_UDP = 256
    # Definitions for user defined Interface
    DEV_USERDEFINED = 261

    # Definitions for user Ethernet Interface
    DEV_VX_ETHERNET1 = 271
    DEV_VX_ETHERNET2 = 272

    # Definitions for user DAIO Interface
    DEV_DAIO_DLL = 280


class DriverType(IntEnum):
    """Value of parameter 'driverType' of subroutine Asap3CreateModule()"""

    ASAP3_DRIVER_UNKNOWN = 0  # Default value for Error case(must not be used)
    ASAP3_DRIVER_CCP = 1  # CCP: CAN calibration protocol
    ASAP3_DRIVER_XCP = 2  # XCP
    ASAP3_DRIVER_CAN = 20  # CAN
    ASAP3_DRIVER_HEXEDIT = 40  # Pure offine driver
    ASAP3_DRIVER_ANALOG = (
        50  # Analog measurement data(e.g. 'National Instruments' PCMCIA - card)
    )
    ASAP3_DRIVER_CANOPEN = 60  # CANopen
    ASAP3_DRIVER_CANDELA = 70  # CANdela Diagnostic
    ASAP3_DRIVER_ENVIRONMENT = 80  # Environment - access to global variables
    ASAP3_DRIVER_LIN = 90  # LIN Driver
    ASAP3_DRIVER_FLX = 100  # FlexRay
    ASAP3_DRIVER_FUNC = 110  # Functonal Diagnostic Driver
    ASAP3_DRIVER_NIDAQMX = 120  # NI DAQ Driver 'National Instruments'
    ASAP3_DRIVER_XCP_RAMSCOPE = 130  # XCP Driver for Ramscope
    ASAP3_DRIVER_SYSTEM = 140  # System driver
    ASAP3_DRIVER_ETH = 150  # Ethernet driver
    ASAP3_DAIO_SYSTEM = 160  # DAIO_SYSTEM driver
    ASAP3_DRIVER_SOME_IP = 170  # SOME-IP driver
    ASAP3_DRIVER_DLT = 180  # DLT driver


class TFormat(IntEnum):
    """Format of ECU measurement or calibration data"""

    ECU_INTERNAL = 0
    PHYSICAL_REPRESENTATION = 1


class ValueType(IntEnum):
    """Valid types of ECU measurement or calibration data"""

    VALUE = 0  # Represents scalar object
    CURVE = 1  # Represents curve object
    MAP = 2  # Represents map object
    AXIS = 3  # Represents axis object
    ASCII = 4  # Represents ASCII string object
    VAL_BLK = 5  # Represents ValueBlock


class ObjectType(IntEnum):
    """Selector to declare an object to be used for measurement or calibration"""

    OTT_MEASURE = 0  # Represents Measurement objects
    OTT_CALIBRATE = 1  # Represents Calibration and writeable Measurement objects
    OTT_UNKNOWN = 2  # Fallback value - should not appear!


class TAsap3DataType(IntEnum):
    """possible datatypes of caracteristic objectes"""

    TYPE_UNKNOWN = 0  # Defaultvalue - should not occur
    TYPE_INT = 1  # Characteristic Object is type of integer
    TYPE_FLOAT = 2  # Characteristic Object is type of float
    TYPE_DOUBLE = 3  # Characteristic Object is type of double
    TYPE_SIGNED = 4  # Characteristic Object is type of signed
    TYPE_UNSIGNED = 5  # Characteristic Object is type of unsigned
    TYPE_STRING = 6  # Characteristic Object is type of ASCII string
    TYPE_INT64 = 7  # Characteristic Object is type of 64bit integer
    TYPE_UINT64 = 8  # Characteristic Object is type of 64bit integer
    TYPE_UWORD = 9  # Characteristic Object is type of unsigned word
    TYPE_WORD = 10  # Characteristic Object is type of signed word
    TYPE_UINT = 11  # Characteristic Object is type of unsigned int
    TYPE_UBYTE = 12  # Characteristic Object is type of BYTE
    TYPE_SBYTE = 13  # Characteristic Object is type of character
    TYPE_FLOAT16 = 14  # Characteristic Object is type of 16bit float


class TAsap3DBOType(IntEnum):
    """possible database object types"""

    DBTYPE_MEASUREMENT = 1  # Selects measurement objects from the database
    DBTYPE_CHARACTERISTIC = 2  # Selects characteristic objects from the database
    DBTYPE_ALL = (
        3  # Selects both, measurement and characteristic objects from the database
    )


class TAsap3ECUState(IntEnum):
    """possible On-Offline states of the ECU"""

    TYPE_SWITCH_ONLINE = 0  # Switches the ECU state from offline to online
    TYPE_SWITCH_OFFLINE = 1  # Switches the ECU state from online to offline


class RecorderType(IntEnum):
    """Typedefinition for Recordertypes"""

    eTRecorderTypeMDF = 0
    eTRecorderTypeILinkRT = 1
    eTRecorderTypeBLF = 2


class RecorderState(IntEnum):
    """Possible states of the Recorder"""

    e_RecConfigure = 0  # Recorder is configured
    e_RecActive = 1  # Recorder is active and ready to run
    e_RecRunning = 2  # Recorder is running
    e_RecPaused = 3  # Recorder paused but measurement is still running
    e_Suspended = 4  # Recorder has stopped


class MeasurementState(IntEnum):
    eT_MEASUREMENT_STOPPED = 0  # Keine Messung
    eT_MEASUREMENT_INIT = 1  # Messung gestartet, Messthread laeuft noch nicht
    eT_MEASUREMENT_STOP_ON_START = 2  # Messung wird in prStart per funktion beendet
    eT_MEASUREMENT_EXIT = 3  # Messung ist gestoppt, aber noch nicht beendet
    eT_MEASUREMENT_THREAD_RUNNING = 4  # Messung gestartet, Messthread laeuft
    eT_MEASUREMENT_RUNNING = 5  # Messschleife laeuft


class EventCode(IntEnum):
    et_ON_DATA_ACQ_START = 0
    et_ON_DATA_ACQ_STOP = 1
    et_ON_BEFORE_DATA_ACQ_START = 2
    et_ON_CLOSEPROJECT = 3
    et_ON_OPENPROJECT = 4
    et_ON_CLOSECANAPE = 5


class DBFileType(IntEnum):
    UNKNOWN = 0
    ASAP2 = 1
    DB = 2
    DBB = 3
    DBC = 4
    CANDELA = 5
    ODF = 6
    EDS = 7
    EHR = 8
    ROB = 9
    LST = 10
    LDF = 11
    CDM = 12
    MDF = 13
    XML = 14
    Update = 15
    CDP = 16
    LostVariable = 17
    PDX = 18
    AutosarXML = 19
    System = 20
    Anonymous = 21
