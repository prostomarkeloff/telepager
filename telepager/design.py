import copy
import typing

from ._compat import KeyboardT, get_inline_button, add_button_to_keyboard

from .manager import PageBook
from .flag import ANY_ORDERING, ANY_QUALITY, FLAG_T
from .i18n import PossibleTexts

from .structs import FORCE_FETCH_ALL, PaginationMessage

if typing.TYPE_CHECKING:
    from .paginator import Record
    from .paginator import PaginatorSettings


def add_ordering_buttons[T](
    pagination_message: PaginationMessage,
    current_keyboard: KeyboardT,
    record: "Record[T]",
    ordering_t: FLAG_T,
    language_code: str,
    settings: "PaginatorSettings",
):
    if pagination_message.show_all_ordering is False:
        message = PaginationMessage(
            page=pagination_message.page,
            user_id=pagination_message.user_id,
            show_all_filters=pagination_message.show_all_filters,
            show_all_ordering=True,
            ordering=pagination_message.ordering,
            quality=pagination_message.quality,
            name=pagination_message.name,
        ).into_callback_data()

        add_button_to_keyboard(
            settings.framework,
            current_keyboard,
            get_inline_button(
                framework=settings.framework,
                text=f"{settings.i18n[PossibleTexts.ORDERING][language_code]} ⬇️",
                callback_data=message,
            ),
        ).row()
    elif pagination_message.show_all_ordering is True:
        message = PaginationMessage(
            page=pagination_message.page,
            user_id=pagination_message.user_id,
            show_all_filters=pagination_message.show_all_filters,
            show_all_ordering=False,
            ordering=pagination_message.ordering,
            quality=pagination_message.quality,
            name=pagination_message.name,
        ).into_callback_data()

        add_button_to_keyboard(
            settings.framework,
            current_keyboard,
            get_inline_button(
                framework=settings.framework,
                text=f"{settings.i18n[PossibleTexts.ORDERING][language_code]} ⬆️",
                callback_data=message,
            ),
        ).row()


        for ordering in ordering_t:
            if ordering.value == pagination_message.ordering:
                shown_name = f"📍 {ordering.shown_name(language_code)}"
                callback_data = settings.noop_callback_data
            else:
                shown_name = ordering.shown_name(language_code)
                callback_data = copy.copy(pagination_message)
                callback_data = PaginationMessage(
                    page=pagination_message.page,
                    user_id=pagination_message.user_id,
                    show_all_filters=pagination_message.show_all_filters,
                    show_all_ordering=pagination_message.show_all_ordering,
                    ordering=ordering.value,
                    quality=pagination_message.quality,
                    name=pagination_message.name,
                ).into_callback_data()

            add_button_to_keyboard(
                settings.framework,
                current_keyboard,
                get_inline_button(
                    framework=settings.framework,
                    text=shown_name,
                    callback_data=callback_data,
                ),
            ).row()


def add_filters_buttons[T](
    pagination_message: PaginationMessage,
    current_keyboard: KeyboardT,
    record: "Record[T]",
    quality_t: FLAG_T,
    language_code: str,
    settings: "PaginatorSettings",
):
    if pagination_message.show_all_filters is False:
        message = PaginationMessage(
            page=pagination_message.page,
            user_id=pagination_message.user_id,
            show_all_filters=True,
            show_all_ordering=pagination_message.show_all_ordering,
            ordering=pagination_message.ordering,
            quality=pagination_message.quality,
            name=pagination_message.name,
        ).into_callback_data()

        add_button_to_keyboard(
            settings.framework,
            current_keyboard,
            get_inline_button(
                framework=settings.framework,
                text=f"{settings.i18n[PossibleTexts.QUALITIES][language_code]} ⬇️",
                callback_data=message,
            ),
        ).row()
    elif pagination_message.show_all_filters is True:
        message = PaginationMessage(
            page=pagination_message.page,
            user_id=pagination_message.user_id,
            show_all_filters=False,
            show_all_ordering=pagination_message.show_all_ordering,
            ordering=pagination_message.ordering,
            quality=pagination_message.quality,
            name=pagination_message.name,
        ).into_callback_data()

        add_button_to_keyboard(
            settings.framework,
            current_keyboard,
            get_inline_button(
                framework=settings.framework,
                text=f"{settings.i18n[PossibleTexts.QUALITIES][language_code]} ⬇️",
                callback_data=message,
            ),
        ).row()

        if pagination_message.quality == ANY_QUALITY:
            all_qualities_text = f"📍 {settings.i18n[PossibleTexts.ALL_QUALITIES][language_code]}"
            all_qualities_callback_data = settings.noop_callback_data
        else:
            all_qualities_text = (
                f"{settings.i18n[PossibleTexts.ALL_QUALITIES][language_code]}"
            )
            all_qualities_callback_data = PaginationMessage(
                page=0,
                user_id=pagination_message.user_id,
                quality=ANY_QUALITY,
                show_all_filters=pagination_message.show_all_filters,
                name=pagination_message.name,
            ).into_callback_data()

        add_button_to_keyboard(
            settings.framework,
            current_keyboard,
            get_inline_button(
                framework=settings.framework,
                text=all_qualities_text,
                callback_data=all_qualities_callback_data,
            ),
        ).row()

        for quality in quality_t:
            if quality.value == pagination_message.quality:
                page = pagination_message.page
                shown_name = f"📍 {quality.shown_name(language_code)}"
                callback_data = settings.noop_callback_data
            else:
                page = 0
                shown_name = quality.shown_name(language_code)
                callback_data = PaginationMessage(
                    page=page,
                    user_id=pagination_message.user_id,
                    quality=quality.value,
                    show_all_filters=pagination_message.show_all_filters,
                    name=pagination_message.name,
                ).into_callback_data()

            add_button_to_keyboard(
                settings.framework,
                current_keyboard,
                get_inline_button(
                    framework=settings.framework,
                    text=shown_name,
                    callback_data=callback_data,
                ),
            ).row()


def add_navigation_buttons[T](
    asked: PaginationMessage,
    keyboard: KeyboardT,
    page_book: PageBook,
    settings: "PaginatorSettings",
):
    # previous if
    if asked.page != 0:
        add_button_to_keyboard(
            settings.framework,
            keyboard,
            get_inline_button(
                framework=settings.framework,
                text="<<",
                callback_data=PaginationMessage(
                    page=0,
                    user_id=asked.user_id,
                    quality=asked.quality,
                    show_all_filters=asked.show_all_filters,
                    show_all_ordering=asked.show_all_ordering,
                    ordering=asked.ordering,
                    name=asked.name,
                ).into_callback_data(),
            ),
        )
        add_button_to_keyboard(
            settings.framework,
            keyboard,
            get_inline_button(
                framework=settings.framework,
                text="<",
                callback_data=PaginationMessage(
                    page=asked.page - 1,
                    user_id=asked.user_id,
                    quality=asked.quality,
                    show_all_filters=asked.show_all_filters,
                    show_all_ordering=asked.show_all_ordering,
                    ordering=asked.ordering,
                    name=asked.name,
                ).into_callback_data(),
            ),
        )

    # show the page count only if there are at least 2 pages
    if len(page_book) > 1:
        add_button_to_keyboard(
            settings.framework,
            keyboard,
            get_inline_button(
                framework=settings.framework,
                text=f"{asked.page + 1}/{len(page_book)}",
                callback_data=settings.noop_callback_data,
            ),
        )

    # next if
    if len(page_book) > asked.page + 1:
        add_button_to_keyboard(
            settings.framework,
            keyboard,
            get_inline_button(
                framework=settings.framework,
                text=">",
                callback_data=PaginationMessage(
                    page=asked.page + 1,
                    user_id=asked.user_id,
                    quality=asked.quality,
                    show_all_filters=asked.show_all_filters,
                    show_all_ordering=asked.show_all_ordering,
                    ordering=asked.ordering,
                    name=asked.name,
                ).into_callback_data(),
            ),
        )
        add_button_to_keyboard(
            settings.framework,
            keyboard,
            get_inline_button(
                framework=settings.framework,
                text=">>",
                callback_data=PaginationMessage(
                    page=FORCE_FETCH_ALL,
                    user_id=asked.user_id,
                    quality=asked.quality,
                    show_all_filters=asked.show_all_filters,
                    show_all_ordering=asked.show_all_ordering,
                    ordering=asked.ordering,
                    name=asked.name,
                ).into_callback_data(),
            ),
        )
