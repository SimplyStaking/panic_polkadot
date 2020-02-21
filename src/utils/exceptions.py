class ApiCallFailedException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnexpectedApiCallErrorException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NoLiveNodeConnectedWithAnApiServerException(Exception):
    pass


class ConfigNotFoundException(Exception):

    def __init__(self, config_file: str) -> None:
        super().__init__('File {} not found.'.format(config_file))


class InitialisationException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class NodeWasNotConnectedToApiServerException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnexpectedApiErrorWhenReadingDataException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConnectionWithNodeApiLostException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidStashAccountAddressException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NoLiveArchiveNodeConnectedWithAnApiServerException(Exception):
    pass


class NodeIsNotAnArchiveNodeException(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)
