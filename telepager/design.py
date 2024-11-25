import copy
import typing

from telegrinder import InlineButton, InlineKeyboard

from .flag import ANY_QUALITY, FLAG_T
from .i18n import PossibleTexts, DEFAULT_LANG_CODE
from .manager import PageBook
from .settings import PaginatorSettings
from .structs import FORCE_FETCH_ALL, PaginationMessage

if typing.TYPE_CHECKING:
    from .paginator import Record


def add_ordering_buttons[T](
    pagination_message: PaginationMessage,
    current_keyboard: InlineKeyboard,
    record: "Record[T]",
    ordering_t: FLAG_T,
    language_code: str,
    settings: PaginatorSettings[T],
):
    if pagination_message.show_all_ordering is False:
        message = pagination_message.copy_with_changed_fields(
            show_all_ordering=True,
        )
        message.show_all_ordering = True

        current_keyboard.add(
            InlineButton(
                text=f"{settings.i18n[PossibleTexts.ORDERING].get(language_code, DEFAULT_LANG_CODE)} ⬇️",
                callback_data=message,
                callback_data_serializer=settings.serializer,
            )
        ).row()
    elif pagination_message.show_all_ordering is True:
        message = pagination_message.copy_with_changed_fields(
            show_all_ordering=False,
        )

        current_keyboard.add(
            InlineButton(
                text=f"{settings.i18n[PossibleTexts.ORDERING].get(language_code, DEFAULT_LANG_CODE)} ⬆️",
                callback_data=message,
                callback_data_serializer=settings.serializer,
            )
        ).row()

        for ordering in ordering_t:
            if ordering.value == pagination_message.ordering:
                shown_name = f"📍 {ordering.shown_name(language_code)}"
                callback_data = settings.empty_callback_data
                serializer = None
            else:
                shown_name = ordering.shown_name(language_code)
                callback_data = copy.copy(pagination_message)
                callback_data = pagination_message.copy_with_changed_fields(
                    ordering=ordering.value,
                )
                serializer = settings.serializer
            current_keyboard.add(
                InlineButton(
                    text=shown_name,
                    callback_data=callback_data,
                    callback_data_serializer=serializer,
                )
            ).row()


def add_filters_buttons[T](
    pagination_message: PaginationMessage,
    current_keyboard: InlineKeyboard,
    record: "Record[T]",
    quality_t: FLAG_T,
    language_code: str,
    settings: PaginatorSettings[T],
):
    if pagination_message.show_all_filters is False:
        message = pagination_message.copy_with_changed_fields(
            show_all_filters=True,
        )

        current_keyboard.add(
            InlineButton(
                text=f"{settings.i18n[PossibleTexts.QUALITIES].get(language_code, DEFAULT_LANG_CODE)} ⬇️",
                callback_data=message,
                callback_data_serializer=settings.serializer,
            )
        ).row()
    elif pagination_message.show_all_filters is True:
        message = pagination_message.copy_with_changed_fields(
            show_all_filters=False,
        )

        current_keyboard.add(
            InlineButton(
                text=f"{settings.i18n[PossibleTexts.QUALITIES].get(language_code, DEFAULT_LANG_CODE)} ⬆️",
                callback_data=message,
                callback_data_serializer=settings.serializer,
            )
        ).row()

        if pagination_message.quality == ANY_QUALITY:
            all_qualities_text = (
                f"📍 {settings.i18n[PossibleTexts.ALL_QUALITIES].get(language_code, DEFAULT_LANG_CODE)}"
            )
            all_qualities_callback_data = "empty"
            serializer = None
        else:
            all_qualities_text = (
                f"{settings.i18n[PossibleTexts.ALL_QUALITIES].get(language_code, DEFAULT_LANG_CODE))}"
            )
            all_qualities_callback_data = pagination_message.copy_with_changed_fields(
                page=0,
                quality=ANY_QUALITY,
            )
            serializer = settings.serializer
        current_keyboard.add(
            InlineButton(
                text=all_qualities_text,
                callback_data=all_qualities_callback_data,
                callback_data_serializer=serializer,
            )
        ).row()

        for quality in quality_t:
            if quality.value == pagination_message.quality:
                page = pagination_message.page
                shown_name = f"📍 {quality.shown_name(language_code)}"
                callback_data = settings.empty_callback_data
                serializer = None
            else:
                page = 0
                shown_name = quality.shown_name(language_code)
                callback_data = pagination_message.copy_with_changed_fields(
                    page=page,
                    quality=quality.value,
                )
                serializer = settings.serializer
            current_keyboard.add(
                InlineButton(
                    text=shown_name,
                    callback_data=callback_data,
                    callback_data_serializer=serializer,
                )
            ).row()


def add_navigation_buttons[T](
    asked: PaginationMessage,
    keyboard: InlineKeyboard,
    page_book: PageBook,
    settings: PaginatorSettings[T],
):
    # previous if
    if asked.page != 0:
        keyboard.add(
            InlineButton(
                text="<<",
                callback_data=asked.copy_with_changed_fields(
                    page=0,
                ),
                callback_data_serializer=settings.serializer,
            )
        )
        keyboard.add(
            InlineButton(
                text="<",
                callback_data=asked.copy_with_changed_fields(
                    page=asked.page - 1,
                ),
                callback_data_serializer=settings.serializer,
            )
        )

    # show the page count only if there are at least 2 pages
    if len(page_book) > 1:
        keyboard.add(
            InlineButton(
                text=f"{asked.page + 1}/{len(page_book)}",
                callback_data=settings.empty_callback_data,
            )
        )

    # next if
    if len(page_book) > asked.page + 1:
        keyboard.add(
            InlineButton(
                text=">",
                callback_data=asked.copy_with_changed_fields(
                    page=asked.page + 1,
                ),
                callback_data_serializer=settings.serializer,
            )
        )
        keyboard.add(
            InlineButton(
                text=">>",
                callback_data=asked.copy_with_changed_fields(
                    page=FORCE_FETCH_ALL,
                ),
                callback_data_serializer=settings.serializer,
            )
        )
