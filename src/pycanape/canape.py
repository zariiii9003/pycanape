import ctypes
from typing import NamedTuple, Dict

from . import RecorderType, MeasurementState
from .recorder import Recorder
from .module import Module
from .cnp_api import cnp_class, cnp_constants, cnp_prototype


class AppVersion(NamedTuple):
    main_version: int
    sub_version: int
    service_pack: int
    app_name: str


class DllVersion(NamedTuple):
    dll_main_version: int
    dll_sub_version: int
    dll_release: int
    os_version: str
    os_release: int


class CANape:
    def __init__(
        self,
        project_path: str,
        fifo_size: int = 128,
        sample_size: int = 256,
        time_out: int = 0,
        clear_device_list: bool = True,
        modal_mode: bool = False,
    ):
        """Initialize and start the CANape runtime environment.

        The first parameter sets the project path where the A2L file and the
        other configuration files are located. The FIFO and sample size buffer
        are used for the measurement buffer. The whole memory is calculated by
        the following formula: Size = FIFO * sample.

        :param project_path:
            Sets the path of the working folder
        :param fifo_size:
            Sets the FIFO buffer size for the measurement
        :param sample_size:
            Sets the sample buffer size for the measurement
        :param time_out:
            Sets the timeout in ms
        :param clear_device_list:
            clear_device_list = True -> all devices are cleared
            clear_device_list = False -> all devices are added,
                which are described in the CANape.ini
        :param modal_mode:
            Sets the start mode of CANape Value:
            modal_mode = True -> non-modal (Python Client and CANape)
            modal_mode = False -> modal (only Python Client)
        """
        asap3_handle = cnp_class.TAsap3Hdl()
        ptr = ctypes.pointer(asap3_handle)

        # fmt: off
        cnp_prototype.Asap3Init5(
            ptr,                                # TAsap3Hdl * hdl,
            time_out,                           # unsigned long responseTimeout,
            project_path.encode('ascii'),       # const char *workingDir,
            fifo_size,                          # unsigned long fifoSize,
            sample_size,                        # unsigned long sampleSize,
            False,                              # bool debugMode,
            clear_device_list,                  # bool clearDeviceList,
            False,                              # bool bHexmode,
            modal_mode,                         # bool bModalMode
        )
        # fmt: on

        self.asap3_handle = ptr.contents

        self._modules: Dict[int, Module] = {}

    def get_application_version(self) -> AppVersion:
        """Call this function to get the current version of the server application."""
        c_app_version = cnp_class.Appversion()
        cnp_prototype.Asap3GetApplicationVersion(
            self.asap3_handle,
            ctypes.byref(c_app_version),
        )
        app_version = AppVersion(
            main_version=c_app_version.MainVersion,
            sub_version=c_app_version.SubVersion,
            service_pack=c_app_version.ServicePack,
            app_name=c_app_version.Application.decode("ascii"),
        )
        return app_version

    @staticmethod
    def get_dll_version() -> DllVersion:
        """Version control"""
        version_t = cnp_class.version_t()
        cnp_prototype.Asap3GetVersion(ctypes.byref(version_t))
        version = DllVersion(
            dll_main_version=version_t.dllMainVersion,
            dll_sub_version=version_t.dllSubVersion,
            dll_release=version_t.dllRelease,
            os_version=version_t.osVersion.decode("ascii"),
            os_release=version_t.osRelease,
        )
        return version

    def get_project_directory(self) -> str:
        """Get the current project Directory."""
        c_buffer = ctypes.create_string_buffer(1024)
        c_length = ctypes.c_ulong(1024)
        cnp_prototype.Asap3GetProjectDirectory(
            self.asap3_handle,
            ctypes.cast(c_buffer, ctypes.c_char_p),
            ctypes.byref(c_length),
        )
        return c_buffer.value.decode("ascii")

    def create_module(
        self,
        module_name: str,
        database_filename: str,
        driver: cnp_constants.DriverType,
        channel: cnp_constants.Channels,
        go_online: bool = True,
        enable_cache: int = -1,
    ) -> Module:
        """The create_module function is used for creating a new
        module/device and for loading an ASAP2 file or a DB file. The function
        configures the logical communication channel which will be used
        (like CCP: 1-4 = CAN1-CAN4) and the driver type like KWPOnCAN, or CCP.
        The return value contains the instance of the Module class.

        Example::

            module = canape.create_module(
                module_name="CCPSim",
                database_filename="C:\\Program Files\\CANape\\CCPsim\\CCPSIM.a2l",
                driver=defines.tDriverType.ASAP3_DRIVER_CCP,
                channel=defines.Channels.DEV_CAN1,
            )

        .. note::
            If the XCP driver is used, the channel for TCP/IP or UDP has to be set
            to the value TCP = 255 or UDP = 256 and for FlexRay = 261.

        :param module_name:
            Name of the module to create
        :param database_filename:
            Sets the path and the name of the a2l or db file
        :param driver:
            Set driver type
        :param channel:
            Set the logical communication channel to be used from CANape
        :param go_online:
            indicates, that the new device need to switched ONLINE
            (allows to create OFFLINE devices)
        :param enable_cache:
            enabled the cache (1) oder disables it (0) if this parameter
            should be ignored it has to be set to (-1)
        :return:
            The instance of the Module class
        """
        module_handle = cnp_class.TModulHdl()

        # fmt: off
        cnp_prototype.Asap3CreateModule3(
            self.asap3_handle,                      # TAsap3Hdl hdl
            module_name.encode('ascii'),            # const char * moduleName
            database_filename.encode('ascii'),      # const char * databaseFilename
            driver.value,                           # short driverType
            channel.value,                          # short channelNo
            go_online,                              # bool goOnline
            enable_cache,                           # short enablecache
            ctypes.byref(module_handle),                                    # TModulHdl * module
        )
        # fmt: on

        if module_handle.value not in self._modules.keys():
            self._modules[module_handle.value] = Module(
                self.asap3_handle, module_handle
            )

        return self._modules[module_handle.value]

    def get_module_count(self) -> int:
        """Returns the count of instantiated Modules in the current Project.

        :return:
            number of modules
        """
        count = ctypes.c_ulong(0)

        cnp_prototype.Asap3GetModuleCount(
            self.asap3_handle,  # TAsap3Hdl hdl
            ctypes.byref(count),  # unsigned long *count
        )
        return count.value

    def get_module_by_name(self, module_name: str) -> Module:
        """Get existing module (created by another application) by name.

        :param module_name:
            name of device
        :return:
            an instance of the Module class
        """
        module_handle = cnp_class.TModulHdl()

        cnp_prototype.Asap3GetModuleHandle(
            self.asap3_handle,  # TAsap3Hdl hdl
            module_name.encode("ascii"),  # const char *moduleName
            ctypes.byref(module_handle),  # TModulHdl * module
        )

        if module_handle.value not in self._modules.keys():
            self._modules[module_handle.value] = Module(
                self.asap3_handle, module_handle
            )

        return self._modules[module_handle.value]

    def get_module_by_index(self, module_index: int) -> Module:
        """Get existing module (created by another application) by index.

        :param module_index:
            index of device
        :return:
            an instance of the Module class
        """
        module_handle = cnp_class.TModulHdl(module_index)

        if module_handle.value not in self._modules.keys():
            self._modules[module_handle.value] = Module(
                self.asap3_handle, module_handle
            )

        return self._modules[module_handle.value]

    def set_interactive_mode(self, mode: bool):
        """Enables the Interactive mode of CANape.

        :param mode:
            Set this parameter to true to enable the interactive
            mode, otherwise set this paramater to false
        """
        cnp_prototype.Asap3SetInteractiveMode(
            self.asap3_handle,  # TAsap3Hdl hdl
            mode,  # bool mode
        )

    def popup_debug_window(self):
        """Trouble shooting: call this function to popup the debug window of the MCD-system."""
        cnp_prototype.Asap3PopupDebugWindow(self.asap3_handle)

    def is_network_activated(self, network_name: str) -> bool:
        """Receives the state a given network interface.

        :param network_name:
            The name of the network as string
        :return:
            state of network (True = active) or (False = disactivated)
        """
        bln = ctypes.c_bool()
        cnp_prototype.Asap3IsNetworkActivated(
            self.asap3_handle, network_name.encode("ascii"), ctypes.byref(bln)
        )
        return bln.value

    def reset_data_acquisition_channels(self):
        """Clears the data acquisition channel list.

        .. note::
           this function only clears these measurement objects from the
           API-Measurement-List which are defined by API
        """
        cnp_prototype.Asap3ResetDataAcquisitionChnls(self.asap3_handle)

    def start_data_acquisition(self):
        """Start data acquisition."""
        cnp_prototype.Asap3StartDataAcquisition(self.asap3_handle)

    def stop_data_acquisition(self):
        """Stop data acquisition."""
        cnp_prototype.Asap3StopDataAcquisition(self.asap3_handle)

    def get_recorder_count(self) -> int:
        """Return count of defined Recorders."""
        c_count = ctypes.c_ulong()
        cnp_prototype.Asap3GetRecorderCount(
            self.asap3_handle,
            ctypes.byref(c_count),
        )
        return c_count.value

    def define_recorder(
        self,
        recorder_name: str,
        recorder_type: RecorderType = RecorderType.eTRecorderTypeMDF,
    ) -> Recorder:
        """Creates a new Recorder.
        :param recorder_name:
            the name of the new Recorder
        :param recorder_type:
            recorder type (e.g. eTRecorderTypeMDF, eTRecorderTypeILinkRT or eTRecorderTypeBLF)
        :return:
            an instance of the `Recorder` class
        """
        c_recorder_id = cnp_class.TRecorderID()
        ptr = ctypes.pointer(c_recorder_id)
        cnp_prototype.Asap3DefineRecorder(
            self.asap3_handle,
            recorder_name.encode("ascii"),
            ptr,
            recorder_type,
        )
        return Recorder(asap3_handle=self.asap3_handle, recorder_id=ptr.contents)

    def get_recorder_by_index(self, index: int) -> Recorder:
        c_recorder_id = cnp_class.TRecorderID()
        ptr = ctypes.pointer(c_recorder_id)
        cnp_prototype.Asap3GetRecorderByIndex(
            self.asap3_handle,
            index,
            ptr,
        )
        return Recorder(asap3_handle=self.asap3_handle, recorder_id=ptr.contents)

    def get_selected_recorder(self) -> Recorder:
        """Retrieve the currently selected Recorder"""
        c_recorder_id = cnp_class.TRecorderID()
        ptr = ctypes.pointer(c_recorder_id)
        cnp_prototype.Asap3GetSelectedRecorder(
            self.asap3_handle,
            ptr,
        )
        return Recorder(asap3_handle=self.asap3_handle, recorder_id=ptr.contents)

    def get_measurement_state(self) -> MeasurementState:
        """Get the current state of the measurement."""
        c_state = cnp_class.enum_type()
        cnp_prototype.Asap3GetMeasurementState(
            self.asap3_handle,
            ctypes.byref(c_state),
        )
        return MeasurementState(c_state.value)

    def has_mcd3_license(self) -> bool:
        """"Check if the MCD option is enabled."""
        c_bln = ctypes.c_bool()
        cnp_prototype.Asap3HasMCD3License(
            self.asap3_handle,
            ctypes.byref(c_bln),
        )
        return c_bln.value

    def exit(self, close_canape: bool = True):
        """Shut down ASAP3 connection to CANape with optional termination of CANape.

        :param close_canape:
            close CANape application if True
        """
        cnp_prototype.Asap3Exit2(
            self.asap3_handle,  # TAsap3Hdl hdl
            close_canape,  # bool close_CANape
        )