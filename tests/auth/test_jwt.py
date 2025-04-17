from loguru import logger
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app_name.config import (
    AppSettings,
    AuthSettings,
    DbSettings,
    LoggingSettings,
    PostgresSettings,
    Settings,
)
from app_name.core.exceptions import BadTokenError
from app_name.cruds.auth.user import get_user_crud
from app_name.models.auth.user import User
from app_name.schemas.auth.token import TokenPair
from app_name.schemas.auth.user import UserFullRead, UserLogin, UserRawCreate
from app_name.services.auth.base import AlchemyTokenAuthService
from app_name.services.auth.current import create_user
from app_name.services.auth.jwt.base import create_expires_map
from app_name.services.auth.jwt.sqlalch import AlchemyJwtAuthLogic


@pytest.fixture(scope="session")
def settings_for_test() -> Settings:
    settings = Settings(
        _env_file=None,
        log=LoggingSettings(level="DEBUG"),
        postgres=PostgresSettings(
            # db="test_app_name"
        ),
        db=DbSettings(),
        app=AppSettings(secret="1" * 32),
        auth=AuthSettings(jwt_access_dt=5, jwt_refresh_dt=10),
    )
    settings.postgres.user = "postgres"
    return settings


@pytest_asyncio.fixture(scope="session")
async def db_SessionMaker(settings_for_test: Settings) -> async_sessionmaker[AsyncSession]:  # type: ignore
    DbEngine = create_async_engine(
        settings_for_test.db_url, echo=settings_for_test.log.level == "TRACE"
    )
    return async_sessionmaker(DbEngine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session(settings_for_test: Settings, db_SessionMaker) -> AsyncSession:  # type: ignore
    async with db_SessionMaker() as session:
        yield session  # type: ignore


@pytest_asyncio.fixture(scope="session")
async def active_user_raw() -> UserRawCreate:
    return UserRawCreate(
        username="active_user",
        password="test123",
        is_admin=False,
        is_active=True,
    )


@pytest_asyncio.fixture(scope="session")
async def admin_user_raw() -> UserRawCreate:
    return UserRawCreate(
        username="admin_user",
        password="test123",
        is_admin=True,
        is_active=True,
    )


@pytest_asyncio.fixture(scope="session")
async def inactive_user_raw() -> UserRawCreate:
    return UserRawCreate(
        username="inactive_user",
        password="test123",
        is_admin=False,
        is_active=False,
    )


@pytest_asyncio.fixture(scope="session")
async def active_user(
    db_SessionMaker: async_sessionmaker[AsyncSession], active_user_raw
):
    async with db_SessionMaker() as session:
        user = await create_user(session, active_user_raw)
        await session.commit()
        yield user
        await get_user_crud().delete(session, id=user.id, force=True)


@pytest_asyncio.fixture(scope="session")
async def admin_user(
    db_SessionMaker: async_sessionmaker[AsyncSession], admin_user_raw
):
    async with db_SessionMaker() as session:
        user = await create_user(session, admin_user_raw)
        await session.commit()
        yield user
        await get_user_crud().delete(session, id=user.id, force=True)


@pytest_asyncio.fixture(scope="session")
async def inactive_user(
    db_SessionMaker: async_sessionmaker[AsyncSession], inactive_user_raw
):
    async with db_SessionMaker() as session:
        user = await create_user(session, inactive_user_raw)
        await session.commit()
        yield user
        await get_user_crud().delete(session, id=user.id, force=True)


@pytest_asyncio.fixture(scope="session")
async def auth_test_service(
    settings_for_test: Settings,
) -> AlchemyTokenAuthService:
    return AlchemyTokenAuthService(
        AlchemyJwtAuthLogic(
            iss=settings_for_test.app.app_name,
            aud=settings_for_test.app.app_name,
            secret=settings_for_test.app.secret,
            expires_map=create_expires_map(
                settings_for_test.auth.jwt_access_dt,
                settings_for_test.auth.jwt_refresh_dt,
            ),
        )
    )


@pytest_asyncio.fixture(scope="module")
async def active_user_token(
    db_SessionMaker: async_sessionmaker[AsyncSession],
    active_user_raw: UserRawCreate,
    auth_test_service: AlchemyTokenAuthService,
    active_user,
) -> TokenPair:
    async with db_SessionMaker() as session:
        res = await auth_test_service.login(
            session,
            UserLogin(
                username=active_user_raw.username,
                password=active_user_raw.password,
            ),
        )
        await session.commit()
        return res


@pytest_asyncio.fixture(scope="module")
async def admin_user_token(
    db_SessionMaker: async_sessionmaker[AsyncSession],
    admin_user_raw: UserRawCreate,
    auth_test_service: AlchemyTokenAuthService,
    admin_user,
) -> TokenPair:
    async with db_SessionMaker() as session:
        res = await auth_test_service.login(
            session,
            UserLogin(
                username=admin_user_raw.username,
                password=admin_user_raw.password,
            ),
        )
        await session.commit()
        return res


@pytest_asyncio.fixture(scope="module")
async def inactive_user_token(
    db_SessionMaker: async_sessionmaker[AsyncSession],
    inactive_user_raw: UserRawCreate,
    auth_test_service: AlchemyTokenAuthService,
    inactive_user,
) -> TokenPair:
    async with db_SessionMaker() as session:
        res = await auth_test_service.login(
            session,
            UserLogin(
                username=inactive_user_raw.username,
                password=inactive_user_raw.password,
            ),
        )
        await session.commit()
        return res


@pytest.mark.asyncio
async def test_get_active_user(
    db_session: AsyncSession,
    active_user_token: TokenPair,
    auth_test_service: AlchemyTokenAuthService,
    active_user: User,
):
    async def pre_test_func():
        user = await auth_test_service.auth(
            db_session, active_user_token.access_token
        )
        if not user.user.is_active:
            raise BadTokenError()
        return user

    ret = await pre_test_func()
    real_active_user = UserFullRead.model_validate(active_user)
    assert ret.user == real_active_user


@pytest.mark.asyncio
async def test_get_admin_user(
    db_session: AsyncSession,
    admin_user_token: TokenPair,
    auth_test_service: AlchemyTokenAuthService,
    admin_user: User,
):
    async def pre_test_func():
        user = await auth_test_service.auth(
            db_session, admin_user_token.access_token
        )
        if not user.user.is_active or not user.user.is_admin:
            raise BadTokenError()
        return user

    ret = await pre_test_func()
    real_active_user = UserFullRead.model_validate(admin_user)
    assert ret.user == real_active_user


@pytest.mark.asyncio
async def test_get_inactive(
    db_session: AsyncSession,
    inactive_user_token: TokenPair,
    auth_test_service: AlchemyTokenAuthService,
    inactive_user: User,
):
    async def pre_test_func():
        user = await auth_test_service.auth(
            db_session, inactive_user_token.access_token
        )
        if not user.user.is_admin:
            raise BadTokenError()
        return user

    got = False
    try:
        await pre_test_func()
    except BadTokenError:
        got = True
    assert got


@pytest_asyncio.fixture(scope="module")
async def expired_active_user_token() -> TokenPair:
    return TokenPair(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc19hZG1pbiI6ZmFsc2UsImlzcyI6ImFwcF9uYW1lIiwic3ViIjoiYWN0aXZlX3VzZXIiLCJhdWQiOiJhcHBfbmFtZSIsImp0aSI6IjFhZjFiZDFmLTIyODctNDAzZS05NDViLWQ2NjdmN2EzN2ZjOSIsInR0eXBlIjoxLCJleHAiOjE3NDQ0NjA4OTAsImlhdCI6MTc0NDQ2MDg5MH0.xC5qmXMGKNA993kFd_fMpt0XLGziqOy9jvwbQn3rCzw",
        refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc19hZG1pbiI6ZmFsc2UsImlzcyI6ImFwcF9uYW1lIiwic3ViIjoiYWN0aXZlX3VzZXIiLCJhdWQiOiJhcHBfbmFtZSIsImp0aSI6ImE5OWJkYTZiLWM2ZjQtNDVhZi1hYzFjLWU2ZTVkM2Y5MmQyNCIsInR0eXBlIjoyLCJleHAiOjE3NDQ0NjExOTAsImlhdCI6MTc0NDQ2MTE5MH0.Ci_CLOCAW6IGEy6YOgqw_L2Q_DB9BY6KD8OQ9RQjus4",
    )


@pytest.mark.asyncio
async def test_not_found_token_for_active_user(
    db_session: AsyncSession,
    expired_active_user_token: TokenPair,
    auth_test_service: AlchemyTokenAuthService,
    active_user: User,
):
    async def pre_test_func():
        user = await auth_test_service.auth(
            db_session, expired_active_user_token.access_token
        )
        if not user.user.is_admin:
            raise BadTokenError()
        return user

    got = False
    try:
        await pre_test_func()
    except BadTokenError:
        got = True
    assert got
