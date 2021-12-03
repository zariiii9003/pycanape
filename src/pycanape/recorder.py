import ctypes
from ctypes import wintypes

from . import RecorderState
from .cnp_api import cnp_class

try:
    from .cnp_api import cnp_prototype
except FileNotFoundError:
    cnp_prototype = None


class Recorder:
    def __init__(
        self, asap3_handle: cnp_class.TAsap3Hdl, recorder_id: cnp_class.TRecorderID
    ):
        if cnp_prototype is None:
            raise FileNotFoundError(
                "CANape API not found. Add CANape API location to environment variable `PATH`."
            )

        self._asap3_handle = asap3_handle
        self._recorder_id = recorder_id

    def get_name(self) -> str:
        """Get the name of the recorder."""
        length = ctypes.c_long(256)
        c_name = ctypes.create_string_buffer(length.value)
        cnp_prototype.Asap3GetRecorderName(
            self._asap3_handle,
            self._recorder_id,
            ctypes.cast(c_name, ctypes.c_char_p),
            ctypes.byref(length),
        )
        return c_name.value.decode("ascii")

    def get_state(self) -> RecorderState:
        """Return the state of a Recorder"""
        c_state = cnp_class.enum_type()
        cnp_prototype.Asap3GetRecorderState(
            self._asap3_handle,
            self._recorder_id,
            ctypes.byref(c_state),
        )
        return RecorderState(c_state.value)

    def is_enabled(self) -> bool:
        """Check if Recorder is enabled.

        :return:
            True if recorder is enabled
        """
        c_bln = ctypes.c_bool()
        cnp_prototype.Asap3IsRecorderEnabled(
            self._asap3_handle,
            self._recorder_id,
            ctypes.byref(c_bln),
        )
        return c_bln.value

    def enable(self):
        """Enable Recorder."""
        cnp_prototype.Asap3EnableRecorder(
            self._asap3_handle,
            self._recorder_id,
            True,
        )

    def disable(self):
        """Disable Recorder."""
        cnp_prototype.Asap3EnableRecorder(
            self._asap3_handle,
            self._recorder_id,
            False,
        )

    def get_mdf_filename(self) -> str:
        """Retrieve the MDF Filename of a Recorder."""
        length = wintypes.DWORD(1024)
        c_name = ctypes.create_string_buffer(length.value)
        cnp_prototype.Asap3GetRecorderMdfFileName(
            self._asap3_handle,
            self._recorder_id,
            ctypes.cast(ctypes.byref(c_name), ctypes.c_char_p),
            ctypes.byref(length),
        )
        return c_name.value.decode("ascii")

    def set_mdf_filename(self, filename: str):
        """Set the MDF Filename for a Recorder.

        :param filename:
            new recorder filename e.g. '{RECORDER}_{YEAR}-{MONTH}-{DAY}_{HOUR}-{MINUTE}-{SECOND}.MF4'
        """
        cnp_prototype.Asap3SetRecorderMdfFileName(
            self._asap3_handle,
            self._recorder_id,
            filename.encode("ascii"),
        )

    def start(self):
        """Starts the recording into the mdf file."""
        print(
            cnp_prototype.Asap3StartRecorder(
                self._asap3_handle,
                self._recorder_id,
            )
        )

    def stop(self, save_to_mdf: bool = True):
        """Stops the recording and writes an MDF File.
        :param save_to_mdf:
            save recorded data to a file if True
        """
        cnp_prototype.Asap3StopRecorder(
            self._asap3_handle,
            self._recorder_id,
            save_to_mdf,
        )

    def pause(self, pause: bool):
        """Pause or unpause recorder."""
        cnp_prototype.Asap3PauseRecorder(
            self._asap3_handle,
            self._recorder_id,
            pause,
        )
