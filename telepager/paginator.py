import dataclasses
import datetime
import typing

from ._compat import (
    API_T,
    KeyboardT,
    MarkupT,
    get_keyboard_t,
    get_markup,
    send_message,
    edit_message,
    merge_keyboards,
)
from .i18n import DEFAULT_I18N, DEFAULT_LANG_CODE, I18N_Text, internationalize, PaginatorInternalI18N
from .structs import FORCE_FETCH_ALL, PageBook, PaginationMessage

from .design import add_filters_buttons, add_navigation_buttons, add_ordering_buttons
from .manager import ABCPageBuilder, Fetcher, FetcherIter, RecordManager
from .flag import ANY_ORDERING, ANY_QUALITY, FLAG_T

FOREVER = datetime.timedelta(days=10000)  # sure bot gets reload


@dataclasses.dataclass
class PaginatorSettings:
    i18n: PaginatorInternalI18N = dataclasses.field(default_factory=lambda: DEFAULT_I18N)

    page_size: int = 10
    incremental_fetching: bool = False
    quality_type: FLAG_T | None = None
    ordering_type: FLAG_T | None = None

    framework: typing.Literal["telegrinder", "aiogram"] = "telegrinder"
    noop_callback_data: str = "empty"


@dataclasses.dataclass
class Record[T]:
    owner_id: int  # id of a user
    expiration_date: datetime.datetime

    manager: RecordManager[T]

    current_page: int  # pages start from 0 cause they appear to us like a list
    asked_quality: int  # INVARIANT: 0 means all
    asked_ordering: int  # INVARIANT: 0 means any
    show_all_filters: bool
    show_all_ordering: bool

    last_message_id_to_edit: int | None = None


class ExpiringStorage[T]:
    def __init__(self) -> None:
        self._inner: dict[int, Record[T]] = {}

    def put(self, record: Record[T]):
        self._inner[record.owner_id] = record

    def get(self, owner_id: int) -> Record[T] | None:
        if owner_id not in self._inner:
            return

        record = self._inner[owner_id]
        is_expired = datetime.datetime.now() >= record.expiration_date
        if is_expired:
            return

        return record

    def __contains__(self, owner_id: int) -> bool:
        return bool(self.get(owner_id))


class Paginator[T]:
    def __init__(
        self,
        *,
        settings: PaginatorSettings | None = None,
    ) -> None:
        self.storage = ExpiringStorage[T]()

        if not settings:
            settings = PaginatorSettings()

        self.settings = settings

    def _get_markup(self, keyboard: KeyboardT | None = None) -> MarkupT | None:
        return get_markup(self.settings.framework, keyboard) if keyboard else None

    async def _send_message(
        self,
        record: Record[T],
        chat_id: int,
        ctx_api: API_T,
        text: str,
        keyboard: KeyboardT | None = None,
        **send_message_kwargs: typing.Any,
    ):
        if not record.last_message_id_to_edit:
            result = await send_message(
                self.settings.framework,
                ctx_api,
                chat_id=chat_id,
                text=text,
                reply_markup=self._get_markup(keyboard),
                **send_message_kwargs,
            )
            record.last_message_id_to_edit = result.message_id
        else:
            await edit_message(
                self.settings.framework,
                ctx_api,
                text=text,
                chat_id=chat_id,
                message_id=record.last_message_id_to_edit,
                reply_markup=self._get_markup(keyboard),
                **send_message_kwargs,
            )

    async def _get_page_book(
        self, *, asked: PaginationMessage, record: Record[T], builder: ABCPageBuilder[T]
    ) -> PageBook:
        # if user clicked ">>" button we have to fetch all existing data
        if asked.page == FORCE_FETCH_ALL:
            await record.manager.fetcher.fetch_all()

        # fetch more pages if user tried like the half of already fetched
        if (
            not record.manager.fetcher.all_fetched()
            and asked.page == record.manager.fetcher.fetched_pages() // 2
        ):
            await record.manager.fetcher.fetch_more()

        page_book = await record.manager.build_page_book(
            asked.quality, asked.ordering, builder, self.settings.quality_type
        )

        # if user clicked ">>" button and we (already) have fetched all data, we have to change a page' number to last **really** existing
        if asked.page == FORCE_FETCH_ALL:
            asked.page = len(page_book) - 1

        return page_book

    async def send_paginated(
        self,
        ctx_api: API_T,
        chat_id: int,
        asked: PaginationMessage,
        fetcher_iter: FetcherIter[T],
        builder: ABCPageBuilder[T],
        empty_page_book_text: I18N_Text | None = None,
        language_code: str = DEFAULT_LANG_CODE,
        extend_keyboard: KeyboardT | None = None,
        ttl: datetime.timedelta = FOREVER,
        **send_message_kwargs: typing.Any,
    ) -> bool:
        keyboard = get_keyboard_t(self.settings.framework)()
        await self.new_record_if_needed(asked, fetcher_iter, ttl)

        record = typing.cast(Record[T], self.storage.get(asked.user_id))

        if self.settings.quality_type:
            add_filters_buttons(
                asked,
                keyboard,
                record,
                self.settings.quality_type,
                language_code,
                self.settings,
            )

        if self.settings.ordering_type:
            add_ordering_buttons(
                asked,
                keyboard,
                record,
                self.settings.ordering_type,
                language_code,
                self.settings,
            )

        page_book = await self._get_page_book(
            asked=asked, record=record, builder=builder
        )

        # if there is no any pages
        if not page_book:
            # if there is no pages AT ALL
            if empty_page_book_text and asked.quality == ANY_QUALITY:
                await send_message(
                    self.settings.framework,
                    ctx_api,
                    chat_id=chat_id,
                    text=internationalize(empty_page_book_text, language_code),
                )
            # if there is no pages for asked quality
            else:
                page = await record.manager.get_empty_page(builder)
                await self._send_message(
                    chat_id=chat_id,
                    ctx_api=ctx_api,
                    record=record,
                    text=page.text,
                    keyboard=keyboard,
                )
            return False

        add_navigation_buttons(asked, keyboard, page_book, self.settings)

        try:
            asked_page = page_book[asked.page]
        except IndexError:  # заебал агрессивно тыкать юзер РЕАЛЬНО
            return False

        if asked_page.keyboard:
            merge_keyboards(self.settings.framework, keyboard, asked_page.keyboard)

        if extend_keyboard:
            merge_keyboards(self.settings.framework, keyboard, extend_keyboard)

        await self._send_message(
            chat_id=chat_id,
            ctx_api=ctx_api,
            record=record,
            text=asked_page.text,
            keyboard=keyboard,
        )

        return True

    async def new_record(
        self,
        owner_id: int,
        fetcher_iter: FetcherIter[T],
        duration: datetime.timedelta = FOREVER,
        current_page: int = 0,
        show_all_filters: bool = False,
        show_all_ordering: bool = False,
        quality: int = ANY_QUALITY,
        ordering: int = ANY_ORDERING,
    ):
        manager = RecordManager[T](
            Fetcher(page_size=self.settings.page_size, iter=fetcher_iter)
        )
        self.storage.put(
            Record(
                owner_id=owner_id,
                manager=manager,
                expiration_date=datetime.datetime.today() + duration,
                current_page=current_page,
                show_all_filters=show_all_filters,
                show_all_ordering=show_all_ordering,
                asked_quality=quality,
                asked_ordering=ordering,
            ),
        )
        if self.settings.incremental_fetching:
            await manager.fetcher.fetch_more()
        else:
            await manager.fetcher.fetch_all()

    async def new_record_from_pagination_message(
        self,
        message: PaginationMessage,
        fetcher_iter: FetcherIter[T],
        duration: datetime.timedelta = FOREVER,
    ):
        await self.new_record(
            fetcher_iter=fetcher_iter,
            owner_id=message.user_id,
            current_page=message.page,
            duration=duration,
        )

    async def new_record_if_needed(
        self,
        message: PaginationMessage,
        fetcher_iter: FetcherIter[T],
        duration: datetime.timedelta = FOREVER,
    ):
        if message.recreate_record:
            await self.new_record_from_pagination_message(
                message, fetcher_iter, duration=duration
            )

        if message.user_id not in self.storage:
            await self.new_record_from_pagination_message(
                message, fetcher_iter, duration=duration
            )
