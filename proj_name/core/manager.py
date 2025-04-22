from typing import Callable, Generic, TypeVar

from proj_name.core.types import SingletonMeta

TCallable = TypeVar("TCallable", bound=Callable)


class BaseDataManager(Generic[TCallable], metaclass=SingletonMeta):
    _map: dict[str, TCallable] = dict()

    @classmethod
    def register(cls, code: str):
        def wrapper(func: TCallable):
            cls._map[code] = func
            return func

        return wrapper

    @classmethod
    def default_func(cls):
        return None

    @classmethod
    def do(cls, code: str, *args, **kwargs):
        if (func := cls._map.get(code, cls.default_func())) is not None:
            return func(*args, **kwargs)
