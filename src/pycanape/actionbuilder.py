import canape


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

    def __init__(self):
        ...

    def __enter__(self):
        ...

    def __exit__(self):
        ...

    def __call__(self):
        ...

    def also(self):
        ...
