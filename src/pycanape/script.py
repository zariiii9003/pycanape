import ctypes
from ctypes import wintypes

from . import RC
from .cnp_api import cnp_class, cnp_constants

try:
    from .cnp_api import cnp_prototype
except FileNotFoundError:
    cnp_prototype = None  # type: ignore[assignment]


class Script:
    def __init__(
        self,
        asap3_handle: cnp_class.TAsap3Hdl,  # type: ignore[valid-type]
        script_handle: cnp_class.TScriptHdl,
    ) -> None:
        """The :class:`~pycanape.module.Script` class is not meant to be instantiated
        by the user. Instead, :class:`~pycanape.module.Script` instances are returned by
        :meth:`~pycanape.module.Module.execute_script_ex`.

        :param asap3_handle:
        :param module_handle:
        """
        if cnp_prototype is None:
            raise FileNotFoundError(
                "CANape API not found. Add CANape API "
                "location to environment variable `PATH`."
            )

        self.asap3_handle = asap3_handle
        self.script_handle = script_handle

    def get_script_state(self) -> cnp_constants.TScriptStatus:
        scrstate = cnp_class.enum_type()
        c_buffer = ctypes.create_string_buffer(1024)
        c_length = ctypes.c_ulong(1024)
        cnp_prototype.Asap3GetScriptState(
            self.asap3_handle,
            self.script_handle,
            ctypes.byref(scrstate),
            ctypes.cast(c_buffer, ctypes.c_char_p),
            ctypes.byref(c_length)
        )

        return dict(
            state=cnp_constants.TScriptStatus(scrstate.value),
            msg=c_buffer.value.decode(RC["ENCODING"])
        )

    def start_script(self) -> None:
        cnp_prototype.Asap3StartScript(
            self.asap3_handle,
            self.script_handle
        )

    def stop_script(self) -> None:
        cnp_prototype.Asap3StopScript(
            self.asap3_handle,
            self.script_handle
        )

    def release_script(self) -> None:
        cnp_prototype.Asap3ReleaseScript(
            self.asap3_handle,
            self.script_handle
        )

    def get_script_result_value(self):
        val = ctypes.c_double()
        cnp_prototype.Asap3GetScriptResultValue(
            self.asap3_handle,
            self.script_handle,
            ctypes.byref(val)
        )
        return val

    def get_script_result_string(self) -> str:
        c_buffer = ctypes.create_string_buffer(1024)
        c_length = ctypes.c_ulong(1024)
        cnp_prototype.Asap3GetScriptResultValue(
            self.asap3_handle,
            self.script_handle,
            ctypes.cast(c_buffer, ctypes.c_char_p),
            ctypes.byref(c_length)
        )
        return c_buffer.value.decode(RC["ENCODING"])
