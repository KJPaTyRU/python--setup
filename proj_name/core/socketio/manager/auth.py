# NOTE: Uncompleted
from proj_name.schemas.auth.user import UserSession


class SioAuthManager:
    """
    This class should be used to manage all socket.io user sessions.
    With this class you can close socket.io user sessions, for example when
    the user has updated the password, downgraded privileges or been deleted.
    """

    def add_user(self, sid: str, user: UserSession):
        pass
