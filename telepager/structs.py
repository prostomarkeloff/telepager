import copy
import typing
from telegrinder.tools import InlineKeyboard
from dataclasses import dataclass

from .flag import ANY_ORDERING, ANY_QUALITY

FORCE_FETCH_ALL = -1  # force fetcher to fetch all lines from iterator
ANY_USER = 0  # that's meant to be replaced, when used for concrete user
NEW_RECORD = -1  # we have to get new record.


@dataclass
class PaginationMessage:
    __key__ = "telepager"

    name: str
    user_id: int = ANY_USER
    record_id: int = NEW_RECORD
    page: int = 0  # page; default value is 0 (pages[0]); -1 is a signal to fetcher to fetch like all data.
    quality: int = ANY_QUALITY  # INVARIANT: 0 means ALL
    ordering: int = ANY_ORDERING  # INVARIANT: 0 means ANY
    show_all_filters: bool = False
    show_all_ordering: bool = False

    def with_replaced_user_id(self, user_id: int) -> typing.Self:
        return self.copy_with_changed_fields(user_id=user_id)

    def for_user(self, user_id: int) -> typing.Self:
        return self.with_replaced_user_id(user_id)

    def copy_with_changed_fields(self, **fields: typing.Any) -> typing.Self:
        s = copy.copy(self)
        for f_name, f_value in fields.items():
            setattr(s, f_name, f_value)

        return s


@dataclass
class Line[T]:
    text: str
    quality: int
    meta: T


@dataclass
class Page:
    text: str
    keyboard: InlineKeyboard | None = None


type FetcherIter[T] = typing.AsyncIterator[Line[T]]
type PageBook = list[Page]
type LinesFittingToPage[T] = list[Line[T]]
type PageSizer[T, *Args] = typing.Callable[
    [list[Line[T]], *Args], typing.Iterator[LinesFittingToPage[T]]
]
type PageSizerFactory[T, *Args] = typing.Callable[[], PageSizer[list[Line[T]], *Args]]

type DefaultFactory[T] = typing.Callable[[], T]
