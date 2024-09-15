import copy
import typing
from dataclasses import dataclass

from .flag import ANY_ORDERING, ANY_QUALITY
from ._compat import KeyboardT

FORCE_FETCH_ALL = -1  # force fetcher to fetch all lines from iterator


def parse_callback_data(inp: str) -> tuple[str, list[str]]:
    parts = inp.split("_")
    try:
        name = parts[0]
    except IndexError:
        raise ValueError("Invalid input passed as a callback data")

    args = parts[1:]

    return name, args


@dataclass
class PaginationMessage:
    name: str
    user_id: int
    page: int = 0  # page; default value is 0 (pages[0]); -1 is a signal to fetcher to fetch like all data.
    quality: int = ANY_QUALITY  # INVARIANT: 0 means ALL
    ordering: int = ANY_ORDERING  # INVARIANT: 0 means ANY
    show_all_filters: bool = False
    show_all_ordering: bool = False
    recreate_record: bool = False

    @classmethod
    def from_callback_data(cls, callback_data: str) -> typing.Self:
        name, args = parse_callback_data(callback_data)
        if len(args) != 7:
            raise ValueError("Invalid input")
        user_id = int(args[0])
        page = int(args[1])
        quality = int(args[2])
        ordering = int(args[3])
        show_all_filters = bool(int(args[4]))
        show_all_ordering = bool(int(args[5]))
        recreate_record = bool(int(args[6]))
        return cls(
            name,
            user_id,
            page,
            quality,
            ordering,
            show_all_filters,
            show_all_ordering,
            recreate_record,
        )

    def into_callback_data(self) -> str:
        return f"{self.name}_{self.user_id}_{self.page}_{self.quality}_{self.ordering}_{int(self.show_all_filters)}_{int(self.show_all_ordering)}_{int(self.recreate_record)}"

    def with_replaced_user_id(self, user_id: int) -> typing.Self:
        s = copy.copy(self)
        s.user_id = user_id
        return s


@dataclass
class Line[T]:
    text: str
    quality: int
    meta: T


@dataclass
class Page:
    text: str
    keyboard: KeyboardT | None = None


type FetcherIter[T] = typing.AsyncIterator[Line[T]]
type PageBook = list[Page]
