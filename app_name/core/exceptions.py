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


# * Auth * #
class AuthException(AppException):
    message: str = "Base Auth Exception"
    code: str = "300"


class TokenParseError(AuthException):
    message: str = "Got bad token"
    code: str = "301"


class BadTokenError(AuthException):
    message: str = "Got bad token"
    code: str = "302"


class TokenValidationError(AuthException):
    message: str = "Got bad token"
    code: str = "303"


class BadLoginCredsError(AuthException):
    message: str = "Got bad login creds"
    code: str = "304"
