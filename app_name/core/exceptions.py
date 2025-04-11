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


class DbException(AppException):
    message: str = "Base Db Exception"
    code: str = "200"


class BadSchemaException(DbException):
    message: str = "Got bad schema"
    code: str = "201"


class BadFilterException(DbException):
    message: str = "Got bad filter"
    code: str = "202"


class BadCreateDataException(DbException):
    message: str = "Got bad create data type"
    code: str = "203"
