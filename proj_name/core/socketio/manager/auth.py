# NOTE: Uncompleted
from proj_name.schemas.auth.user import UserSession


class SioAuthManager:
    """
    This class should be used to manage all socket.io user sessions.
    With this class you can close socket.io user sessions, for example when
    the user has updated the password, downgraded privileges or been deleted.
    """

    # Context functions

    # def user_sid_constructor(self, username: str) -> str:
    #     return "global_" + username

    # async def set_context(
    #     self,
    #     sid: str,
    #     ctx: AuthSioCtxType,
    #     store_to_user: bool = True,
    #     **kwargs,
    # ):
    #     ctx_data = ctx.model_dump(mode="python")
    #     await self.save_session(sid, ctx_data)
    #     if store_to_user:
    #         user_sid = self.user_sid_constructor(ctx.user.user.username)

    #         # TODO: there is a race condition.
    #         # NOTE: Use Global lock (depends on session manager) to improve it
    #         user_ctx: dict = await self.get_session(user_sid)
    #         sids: set = user_ctx.get("sids", set())
    #         sids.add(user_sid)
    #         await self.save_session(user_sid, dict(sids=sids))

    # async def get_context(self, sid: str) -> AuthSioCtxType:
    #     return self._ctx_class.model_validate(await self.get_session(sid))

    def add_user(self, sid: str, user: UserSession):
        pass
