import ctypes
from typing import TYPE_CHECKING, Optional

from .cnp_api import cnp_class, cnp_constants
from .cnp_api.cnp_constants import ASAP3_INVALID_MODULE_HDL
from .cnp_api.cnp_prototype import CANapeDll
from .config import RC

if TYPE_CHECKING:
    from .module import Module


class Script:
    def __init__(
        self,
        dll: CANapeDll,
        asap3_handle: cnp_class.TAsap3Hdl,  # type: ignore[valid-type]
        script_handle: cnp_class.TScriptHdl,
    ) -> None:
        """The :class:`~pycanape.script.Script` class is not meant to be instantiated
        by the user. Instead, :class:`~pycanape.script.Script` instances are returned by
        :meth:`~pycanape.module.Module.execute_script_ex`.

        :param asap3_handle:
        :param script_handle:
        """
        self._dll = dll
        self.asap3_handle = asap3_handle
        self.script_handle = script_handle

    def get_script_state(self) -> cnp_constants.TScriptStatus:
        """Returns the state of a script.

        :return:
            current state of the script
        """
        scrstate = cnp_class.enum_type()
        max_size = ctypes.c_ulong(0)
        self._dll.Asap3GetScriptState(
            self.asap3_handle,
            self.script_handle,
            ctypes.byref(scrstate),
            None,
            ctypes.byref(max_size),
        )
        return cnp_constants.TScriptStatus(scrstate.value)

    def start_script(
        self,
        *,
        command_line: Optional[str] = None,
        current_device: Optional["Module"] = None,
    ) -> None:
        """Starts the script.

        :param command_line:
            Set a commandline for the script.
        :param current_device:
            Set a module as current_device.
        """
        module_handle = (
            current_device.module_handle
            if current_device
            else cnp_class.TModulHdl(ASAP3_INVALID_MODULE_HDL)
        )
        _command_line = command_line.encode(RC["ENCODING"]) if command_line else None
        self._dll.Asap3StartScript(
            self.asap3_handle,
            self.script_handle,
            _command_line,
            module_handle,
        )

    def stop_script(self) -> None:
        """Stop the script."""
        self._dll.Asap3StopScript(
            self.asap3_handle,
            self.script_handle,
        )

    def release_script(self) -> None:
        """Removes a declared script from the Tasklist.
        To receive the result you must use the 'SetScriptResult' in
        your CASL script."""
        self._dll.Asap3ReleaseScript(
            self.asap3_handle,
            self.script_handle,
        )

    def get_script_result_value(self) -> float:
        """Returns the exitcode of a script.

        :return:
            result value of the script
        """
        val = ctypes.c_double()
        self._dll.Asap3GetScriptResultValue(
            self.asap3_handle,
            self.script_handle,
            ctypes.byref(val),
        )
        return val.value

    def get_script_result_string(self) -> str:
        """Returns a script result.

        :return:
            result string of the script
        """
        length = ctypes.c_ulong()
        self._dll.Asap3GetScriptResultString(
            self.asap3_handle,
            self.script_handle,
            None,
            ctypes.byref(length),
        )
        buffer = ctypes.create_string_buffer(length.value)
        self._dll.Asap3GetScriptResultString(
            self.asap3_handle,
            self.script_handle,
            buffer,
            ctypes.byref(length),
        )
        return buffer.value.decode(RC["ENCODING"])
