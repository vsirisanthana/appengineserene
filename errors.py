class Http4xx(Exception):
    """Base HTTP 4xx Client Error
    """
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


class ContentTypeNotSupportedError(Exception):
    """
    """