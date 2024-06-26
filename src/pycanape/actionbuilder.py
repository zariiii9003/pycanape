from typing import Callable, Optional, Union

from .canape import CANape

CanapeAction = Union[Callable[[CANape], CANape], "ActionBuilder"]


class ActionBuilder:
    """Use of the CANape API
    locks the user out of the
    application for the duration
    of the use. The purpose for
    this class is to wrap the api
    so that the time the program
    spends locking the application
    from the user is minimized.

    All attributes correspond to
    arguments of the CANape class
    and serve to pass through the
    options to the constructor.

    Attributes:
    close_canape: bool
        When called with this set
        to true, on closing connection
        to CANape on action completion,
        CANape will close.
    project_path: str
        You must set this to the path
        to the CANape project before
        performing the action.
    modal_mode: bool
        Whether or not to connect to
        CANape in modal mode. What this
        means isn't clearly documented.

    canape: Optional[CANape]
        This attribute is special and is
        used only to allow the inner CANape
        connection to be used within a
        with block as a context manager.
        At all times except under a with
        block this will be functionally
        None.
    """

    close_canape: bool
    project_path: str
    modal_mode: bool

    canape: Optional[CANape]

    def __init__(self, _action: CanapeAction = lambda x: x):
        self._action = _action

    def __enter__(self):
        self.canape = CANape(self.project_path, self.modal_mode)

    def __exit__(self, primus, secundus, tertius):
        # It is apropriate to ignore the below line for
        # typing because __exit__ should only be called
        # after __enter__, and __enter__ ensures context
        # is not None. It is notable that the user can
        # screw around but I don't need to worry about
        # that.
        self.canape.exit(self.close_canape)  # type: ignore

    def __call__(self, canape: Optional[CANape] = None) -> CANape:
        """Using this wrapper will lock
        the application only for the
        duration of this function.
        This function ultimately returns
        a closed CANape object IE. unusable."""
        if canape is None:
            self.canape = CANape(self.project_path, self.modal_mode)
            self._action(self.canape)
            canape.exit(self.close_canape)
            return canape
        else:
            self._action(canape)
            return canape

    def also(self, next_action: CanapeAction) -> "ActionBuilder":
        """This function allows the chaining of
        multiple operations into the same lock window."""
        return ActionBuilder(lambda x: next_action(self._action(x)))
