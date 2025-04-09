class AppException(Exception):
    message: str = "Base App Exception"
    code: str = "100"

    def __init__(self, message: str = "", **kwargs):
        self.details = kwargs
        self.details["code"] = self.code
        message = message or self.message
        message = ("[{code}] " + message).format(**self.details)
        self.details["message"] = message
        super().__init__(message)
