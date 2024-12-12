import datetime
import typing

from telegrinder import (
    API,
    CallbackQueryCute,
    HTMLFormatter,
    InlineQueryCute,
    MessageCute,
)
from telegrinder.tools.keyboard import InlineKeyboard

from telepager.i18n import I18N_Text, internationalize

from .design import add_filters_buttons, add_navigation_buttons, add_ordering_buttons
from .flag import ANY_QUALITY
from .manager import ABCPageBuilder, Fetcher, FetcherIter, RecordManager
from .settings import PaginatorSettings
from .storage import ABCExpiringStorage, InMemoryExpiringStorage
from .structs import FORCE_FETCH_ALL, NEW_RECORD, PageBook, PaginationMessage, Record


def _not_loaded_defaults_exception(name: str) -> typing.NoReturn:
    raise RuntimeError(
        f"You've tried to use the default {name}, but it isn't set\nSet the default or pass to 'send_paginated' the needed value."
    )


def _get_ctx_api_and_chat_id_from_event(
    event: MessageCute | CallbackQueryCute | InlineQueryCute,
) -> tuple[API, int]:
    if isinstance(event, MessageCute):
        return event.api, event.chat_id
    elif isinstance(event, CallbackQueryCute):
        return event.api, event.chat_id.unwrap()
    else:
        return event.api, event.from_user.id

EventOrPairT = (MessageCute | CallbackQueryCute | InlineQueryCute) | tuple[API, int]

class Paginator[T]:
    def __init__(
        self,
        settings: PaginatorSettings[T],
        storage: ABCExpiringStorage[T] | None = None,
    ) -> None:
        self.storage = storage or InMemoryExpiringStorage[T]()
        self.settings = settings

        self.initial_message = settings.initial_message

    async def _send_message(
        self,
        record: Record[T],
        chat_id: int,
        ctx_api: API,
        text: str,
        keyboard: InlineKeyboard | None = None,
        **telegram_api_additional: typing.Any,
    ):
        if not record.last_message_id_to_edit:
            result = await ctx_api.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard.get_markup() if keyboard else None,
                parse_mode=HTMLFormatter.PARSE_MODE,
                **telegram_api_additional
            )
            record.last_message_id_to_edit = result.unwrap().message_id
        else:
            await ctx_api.edit_message_text(
                text=text,
                chat_id=chat_id,
                message_id=record.last_message_id_to_edit,
                reply_markup=keyboard.get_markup() if keyboard else None,
                parse_mode=HTMLFormatter.PARSE_MODE,
                **telegram_api_additional
            )

    async def _get_page_book(
        self,
        *,
        asked: PaginationMessage,
        record: Record[T],
        builder: ABCPageBuilder[T],
    ) -> PageBook:
        # if user clicked ">>" button we have to fetch all existing data
        if asked.page == FORCE_FETCH_ALL:
            await record.manager.fetcher.fetch_all()

        # fetch more pages if user tried like the half of already fetched
        if (
            not record.manager.fetcher.all_fetched()
            and record.manager.fetcher.fetched_pages
            and asked.page == record.manager.fetcher.fetched_pages // 2
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
        event_or_pair: EventOrPairT,
        asked: PaginationMessage,
        fetcher_iter: FetcherIter[T] | None = None,
        builder: ABCPageBuilder[T] | None = None,
        empty_page_book_text: I18N_Text | None = None,
        language_code: str | None = None,
        extend_keyboard: InlineKeyboard | None = None,
        ttl: datetime.timedelta | None = None,
        **telegram_api_additional: typing.Any,
    ) -> bool:
        keyboard = InlineKeyboard()

        if isinstance(event_or_pair, tuple):
            ctx_api, chat_id = event_or_pair[0], event_or_pair[1]
        else:
            ctx_api, chat_id = _get_ctx_api_and_chat_id_from_event(event_or_pair)

        if not fetcher_iter:
            fetcher_iter = (
                self.settings.default_fetcher_factory()
                if self.settings.default_fetcher_factory
                else _not_loaded_defaults_exception("fetcher_iter")
            )
        if not builder:
            builder = (
                self.settings.default_page_builder
                if self.settings.default_page_builder
                else _not_loaded_defaults_exception("builder")
            )
        if not empty_page_book_text:
            empty_page_book_text = self.settings.default_empty_page_book_text
        if not language_code:
            language_code = self.settings.default_language_code
        if not ttl:
            ttl = self.settings.default_ttl

        # here we do the IMPORTANT thing, that lets us to have different working keyboards at a time
        # we change the pagination message for design.py, letting it work with CORRECT record_id
        # cause there is a variant, when asked.record_id is NEW_RECORD, so we have to change it to
        # an actual record id
        # we do the copy, cause we don't want to touch the initial message.
        record = await self.get_or_create_record_if_needed(asked, fetcher_iter, ttl)
        asked = asked.copy_with_changed_fields(record_id=record.record_id)

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
                await ctx_api.send_message(
                    chat_id=chat_id,
                    text=internationalize(empty_page_book_text, language_code),
                    parse_mode=HTMLFormatter.PARSE_MODE,
                    **telegram_api_additional
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
                    **telegram_api_additional
                )
            return False

        add_navigation_buttons(asked, keyboard, page_book, self.settings)

        try:
            asked_page = page_book[asked.page]
        except IndexError:
            return False

        if asked_page.keyboard:
            keyboard.merge(asked_page.keyboard)

        if extend_keyboard:
            keyboard.merge(extend_keyboard)

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
        duration: datetime.timedelta,
        record_id: int | None = None,
    ) -> Record[T]:
        manager = RecordManager[T](
            Fetcher(
                incremental_fetching_step=self.settings.incremental_fetching_step,
                iter=fetcher_iter,
            ),
            self.settings,
        )
        expiration_date = datetime.datetime.today() + duration

        if record_id is not None:
            record = Record[T](
                owner_id=owner_id,
                manager=manager,
                expiration_date=expiration_date,
                record_id=record_id,
            )
        else:
            record = Record[T].with_generated_record_id(
                storage=self.storage,
                owner_id=owner_id,
                manager=manager,
                expiration_date=expiration_date,
            )
        self.storage.put(record)
        if self.settings.incremental_fetching:
            await manager.fetcher.fetch_more()
        else:
            await manager.fetcher.fetch_all()

        return record

    async def new_record_from_pagination_message(
        self,
        message: PaginationMessage,
        fetcher_iter: FetcherIter[T],
        duration: datetime.timedelta,
        record_id: int | None = None,
    ) -> Record[T]:
        return await self.new_record(
            fetcher_iter=fetcher_iter,
            owner_id=message.user_id,
            duration=duration,
            record_id=record_id,
        )

    async def get_or_create_record_if_needed(
        self,
        message: PaginationMessage,
        fetcher_iter: FetcherIter[T],
        duration: datetime.timedelta,
    ) -> Record[T]:
        # if we are asked to create the new record
        if message.record_id == NEW_RECORD:
            return await self.new_record_from_pagination_message(
                message, fetcher_iter, duration=duration
            )

        # if expired or doesn't exist in our current storage
        if not self.storage.get_record(message.user_id, message.record_id):
            return await self.new_record_from_pagination_message(
                message, fetcher_iter, duration=duration, record_id=message.record_id
            )

        return typing.cast(
            Record[T], self.storage.get_record(message.user_id, message.record_id)
        )
