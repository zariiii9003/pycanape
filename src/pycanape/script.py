import ctypes

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
        """The :class:`~pycanape.script.Script` class is not meant to be instantiated
        by the user. Instead, :class:`~pycanape.script.Script` instances are returned by
        :meth:`~pycanape.module.Module.execute_script_ex`.

        :param asap3_handle:
        :param script_handle:
        """
        if cnp_prototype is None:
            err_msg = (
                "CANape API not found. Add CANape API "
                "location to environment variable `PATH`."
            )
            raise FileNotFoundError(err_msg)

        self.asap3_handle = asap3_handle
        self.script_handle = script_handle

    def get_script_state(self) -> cnp_constants.TScriptStatus:
        """Returns the state of a script.

        :return:
            current state of the script
        """
        scrstate = cnp_class.enum_type()
        max_size = ctypes.c_ulong(0)
        cnp_prototype.Asap3GetScriptState(
            self.asap3_handle,
            self.script_handle,
            ctypes.byref(scrstate),
            None,
            ctypes.byref(max_size),
        )
        return cnp_constants.TScriptStatus(scrstate.value)

    def start_script(self) -> None:
        """Starts the script."""
        cnp_prototype.Asap3StartScript(
            self.asap3_handle,
            self.script_handle,
        )

    def stop_script(self) -> None:
        """Stop the script."""
        cnp_prototype.Asap3StopScript(
            self.asap3_handle,
            self.script_handle,
        )

    def release_script(self) -> None:
        """Removes a declared script from the Tasklist.
        To receive the result you must use the 'SetScriptResult' in
        your CASL script."""
        cnp_prototype.Asap3ReleaseScript(
            self.asap3_handle,
            self.script_handle,
        )

    def get_script_result_value(self) -> float:
        """Returns the exitcode of a script.

        :return:
            result value of the script
        """
        val = ctypes.c_double()
        cnp_prototype.Asap3GetScriptResultValue(
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
        # call function first time to determine max_size
        max_size = ctypes.c_ulong(0)
        cnp_prototype.Asap3GetScriptResultString(
            self.asap3_handle,
            self.script_handle,
            None,
            ctypes.byref(max_size),
        )

        # call function again to retrieve data
        c_buffer = ctypes.create_string_buffer(max_size.value)
        cnp_prototype.Asap3GetScriptResultString(
            self.asap3_handle,
            self.script_handle,
            c_buffer,
            ctypes.byref(max_size),
        )
        return c_buffer.value.decode(RC["ENCODING"])
