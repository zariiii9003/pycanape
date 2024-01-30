from typing import Optional, Union, Callable
import canape

CanapeAction = Union[Callable[[canape], canape], 'ActionBuilder']


class ActionBuilder:
    """Use of the CANape API
    locks the user out of the
    application for the duration
    of the use. The purpose for
    this class is to wrap the api
    so that the time the program
    spends locking the application
    from the user is minimized.
    """

    close_canape: bool
    project_path: str
    modal_mode: bool

    context: Optional[canape.CANape]

    def __init__(self, _action: CanapeAction = lambda x: x):
        self._action = _action

    def __enter__(self):
        self.context = canape.CANape(self.project_path, self.modal_mode)
        # TODO: figure out using context directly as CANape object.

    def __exit__(self):
        self.context.exit(self.close_canape)

    def __call__(self, context: Optional[CanapeAction] = None):
        """Using this wrapper will lock
        the application only for the
        duration of this function."""
        if context is None:
            context = canape.CANape(self.project_path, self.modal_mode)
            self._action(context)
            context.exit(self.close_canape)
        else:
            self._action(context)
            return context

    def also(self, next_action: CanapeAction) -> 'ActionBuilder':
        """This function allows the chaining of
        multiple operations into the same lock window."""
        return ActionBuilder(lambda x: next_action(self._action(x)))
