# SPDX-FileCopyrightText: 2022-present Artur Drogunow <artur.drogunow@zf.com>
#
# SPDX-License-Identifier: MIT

import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Union

from .cnp_api import cnp_class, cnp_constants
from .cnp_api.cnp_prototype import CANapeDll
from .config import RC


class Recorder:
    def __init__(
        self,
        dll: CANapeDll,
        asap3_handle: cnp_class.TAsap3Hdl,  # type: ignore[valid-type]
        recorder_id: cnp_class.TRecorderID,  # type: ignore[valid-type]
    ) -> None:
        """The :class:`~pycanape.recorder.Recorder` class is not meant to be instantiated
        by the user. :class:`~pycanape.recorder.Recorder` instances are returned by
        :meth:`~pycanape.canape.CANape.define_recorder`,
        :meth:`~pycanape.canape.CANape.get_recorder_by_index` and
        :meth:`~pycanape.canape.CANape.get_selected_recorder`.

        :param asap3_handle:
        :param recorder_id:
        """

        self._dll = dll
        self._asap3_handle = asap3_handle
        self._recorder_id = recorder_id

    def get_name(self) -> str:
        """Get the name of the recorder."""
        length = ctypes.c_long()
        self._dll.Asap3GetRecorderName(
            self._asap3_handle,
            self._recorder_id,
            None,
            ctypes.byref(length),
        )
        buffer = ctypes.create_string_buffer(length.value)
        self._dll.Asap3GetRecorderName(
            self._asap3_handle,
            self._recorder_id,
            buffer,
            ctypes.byref(length),
        )
        return buffer.value.decode(RC["ENCODING"])

    def get_state(self) -> cnp_constants.RecorderState:
        """Return the state of a Recorder"""
        c_state = cnp_class.enum_type()
        self._dll.Asap3GetRecorderState(
            self._asap3_handle,
            self._recorder_id,
            ctypes.byref(c_state),
        )
        return cnp_constants.RecorderState(c_state.value)

    def is_enabled(self) -> bool:
        """Check if Recorder is enabled.

        :return:
            True if recorder is enabled
        """
        c_bln = ctypes.c_bool()
        self._dll.Asap3IsRecorderEnabled(
            self._asap3_handle,
            self._recorder_id,
            ctypes.byref(c_bln),
        )
        return c_bln.value

    def enable(self) -> None:
        """Enable Recorder."""
        self._dll.Asap3EnableRecorder(
            self._asap3_handle,
            self._recorder_id,
            True,
        )

    def disable(self) -> None:
        """Disable Recorder."""
        self._dll.Asap3EnableRecorder(
            self._asap3_handle,
            self._recorder_id,
            False,
        )

    def get_mdf_filename(self) -> str:
        """Retrieve the MDF Filename of a Recorder."""
        length = wintypes.DWORD()
        self._dll.Asap3GetRecorderMdfFileName(
            self._asap3_handle,
            self._recorder_id,
            None,
            ctypes.byref(length),
        )
        buffer = ctypes.create_string_buffer(length.value)
        self._dll.Asap3GetRecorderMdfFileName(
            self._asap3_handle,
            self._recorder_id,
            buffer,
            ctypes.byref(length),
        )
        return buffer.value.decode(RC["ENCODING"])

    def set_mdf_filename(self, filename: Union[str, Path]) -> None:
        """Set the MDF Filename for a Recorder.

        :param filename:
            new recorder filename e.g. '{RECORDER}_{YEAR}-{MONTH}-{DAY}_{HOUR}-{MINUTE}-{SECOND}.MF4'
        """
        self._dll.Asap3SetRecorderMdfFileName(
            self._asap3_handle,
            self._recorder_id,
            str(filename).encode(RC["ENCODING"]),
        )

    def start(self) -> None:
        """Starts the recording into the mdf file."""
        self._dll.Asap3StartRecorder(
            self._asap3_handle,
            self._recorder_id,
        )

    def stop(self, save_to_mdf: bool = True) -> None:
        """Stops the recording and writes an MDF File.

        :param save_to_mdf:
            save recorded data to a file if True
        """
        self._dll.Asap3StopRecorder(
            self._asap3_handle,
            self._recorder_id,
            save_to_mdf,
        )

    def pause(self, pause: bool) -> None:
        """Pause or unpause recorder."""
        self._dll.Asap3PauseRecorder(
            self._asap3_handle,
            self._recorder_id,
            pause,
        )
