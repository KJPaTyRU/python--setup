class AppException(Exception):
    message: str = "Base App Exception"
    code: str = "100"
    status: int = 500

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
    status: int = 422


class BadFilterException(DbException):
    message: str = "Got bad filter"
    code: str = "202"
    status: int = 422


class BadCreateDataException(DbException):
    message: str = "Got bad create data type"
    code: str = "203"
    status: int = 422


# * Auth * #
class AuthException(AppException):
    message: str = "Base Auth Exception"
    code: str = "300"
    status: int = 403


class TokenParseError(AuthException):
    message: str = "Got bad token"
    code: str = "301"
    status: int = 422


class BadTokenError(AuthException):
    message: str = "Got bad token"
    code: str = "302"
    status: int = 422


class TokenValidationError(AuthException):
    message: str = "Got bad token"
    code: str = "303"
    status: int = 422


class BadLoginCredsError(AuthException):
    message: str = "Got bad login creds"
    code: str = "304"
    status: int = 422
