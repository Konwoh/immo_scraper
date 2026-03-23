class ParsingError(Exception):
    """Exception raised for Error while parsing data.

    Args:
        message: error message
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RequestError(Exception):
    """Exception raised while sending Request

    Args:
        Message: error message
    """
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)