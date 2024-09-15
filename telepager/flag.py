import abc
import enum
import typing

ANY_QUALITY: int = 0
ANY_ORDERING: int = ANY_QUALITY


class ABCFlagMeta(abc.ABCMeta, enum.EnumMeta):
    def __new__(mcls, *args, **kw):  # type: ignore
        abstract_enum_cls = super().__new__(mcls, *args, **kw)  # type: ignore
        # Only check abstractions if members were defined.
        if abstract_enum_cls._member_map_:
            try:  # Handle existence of undefined abstract methods.
                absmethods = list(abstract_enum_cls.__abstractmethods__)
                if absmethods:
                    missing = ", ".join(f"{method!r}" for method in absmethods)
                    plural = "s" if len(absmethods) > 1 else ""
                    raise TypeError(
                        f"cannot instantiate abstract class {abstract_enum_cls.__name__!r}"
                        f" with abstract method{plural} {missing}"
                    )
            except AttributeError:
                pass
        return abstract_enum_cls


class Flag(enum.IntFlag, metaclass=ABCFlagMeta, boundary=enum.STRICT):
    @abc.abstractmethod
    def shown_name(self, language_code: str) -> str: ...


FLAG_T: typing.TypeAlias = typing.Type[Flag]
Quality = Flag
Ordering = Flag
