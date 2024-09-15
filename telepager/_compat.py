import typing

_aiogram = False
try:
    import aiogram as __aiogram  # type: ignore

    _aiogram = True
except ImportError:
    pass

_telegrinder = False
try:
    import telegrinder as __telegrinder  # type: ignore

    _telegrinder = True
except ImportError:
    pass

if typing.TYPE_CHECKING:
    if _aiogram:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import (
            InlineKeyboardMarkup as AG_InlineKeyboardMarkup,
            Message as AG_Message,
            InlineKeyboardButton,
        )
        from aiogram import Bot
    if _telegrinder:
        from telegrinder import InlineKeyboard, InlineButton
        from telegrinder.types.objects import (
            InlineKeyboardMarkup as TG_InlineKeyboardMarkup,
            Message as TG_Message,
        )
        from telegrinder import API


type KeyboardT = "InlineKeyboardBuilder | InlineKeyboard"
type API_T = "Bot | API"
type MarkupT = "AG_InlineKeyboardMarkup | TG_InlineKeyboardMarkup"
type MessageT = "AG_Message | TG_Message"
type ButtonT = "InlineKeyboardButton | InlineButton"


def _exception(name: str):
    raise RuntimeError(
        f"You've tried to use the {name} framework, but it seems it isn't installed in your venv"
    )


def is_telegrinder() -> bool:
    return _telegrinder


def is_aiogram() -> bool:
    return _aiogram


def get_keyboard_t(framework: str) -> typing.Type[KeyboardT]:
    if framework == "aiogram":
        if not _aiogram:
            _exception(framework)

        from aiogram.utils.keyboard import InlineKeyboardBuilder

        return InlineKeyboardBuilder

    if framework == "telegrinder":
        if not _telegrinder:
            _exception(framework)

        from telegrinder import InlineKeyboard

        return InlineKeyboard

    else:
        raise RuntimeError(f"{framework} is not supported by telepager")


def get_markup(framework: str, keyboard: KeyboardT) -> MarkupT:
    if framework == "aiogram":
        keyboard = typing.cast("InlineKeyboardBuilder", keyboard)
        return keyboard.as_markup()
    else:
        keyboard = typing.cast("InlineKeyboard", keyboard)
        return keyboard.get_markup()


async def send_message(
    framework: str, ctx_api: API_T, **kwargs: typing.Any
) -> MessageT:
    if framework == "aiogram":
        ctx_api = typing.cast("Bot", ctx_api)
        return await ctx_api.send_message(**kwargs)
    else:
        ctx_api = typing.cast("API", ctx_api)
        result = await ctx_api.send_message(**kwargs)
        return result.unwrap()


async def edit_message(framework: str, ctx_api: API_T, **kwargs: typing.Any):
    if framework == "aiogram":
        ctx_api = typing.cast("Bot", ctx_api)
        return await ctx_api.edit_message_text(**kwargs)
    else:
        ctx_api = typing.cast("API", ctx_api)
        result = await ctx_api.edit_message_text(**kwargs)
        return result.unwrap()


def merge_keyboards(framework: str, merge_into: KeyboardT, merge_from: KeyboardT):
    if framework == "aiogram":
        merge_into = typing.cast("InlineKeyboardBuilder", merge_into)
        merge_from = typing.cast("InlineKeyboardBuilder", merge_from)
        merge_into.attach(merge_from)
    else:
        merge_into = typing.cast("InlineKeyboard", merge_into)
        merge_from = typing.cast("InlineKeyboard", merge_from)
        merge_into.merge(merge_from)


def get_inline_button(framework: str, text: str, callback_data: str) -> ButtonT:
    if framework == "aiogram":
        from aiogram.types import InlineKeyboardButton

        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        return button
    else:
        from telegrinder import InlineButton

        return InlineButton(text=text, callback_data=callback_data)


def add_button_to_keyboard(
    framework: str, keyboard: KeyboardT, button: ButtonT
) -> KeyboardT:
    if framework == "aiogram":
        keyboard = typing.cast("InlineKeyboardBuilder", keyboard)
        button = typing.cast("InlineKeyboardButton", button)
        keyboard.add(button)
        return keyboard
    else:
        keyboard = typing.cast("InlineKeyboard", keyboard)
        button = typing.cast("InlineButton", button)
        keyboard.add(button)
        return keyboard
