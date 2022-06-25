class MikroJException(Exception):
    """
    Base class for all exceptions in mikroj.
    """

    pass


class NotStartedError(MikroJException):
    """
    Raised when ImageJ is not started.
    """

    pass
