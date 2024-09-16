import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from base import fetcher, paginator, INITIAL_MESSAGE, PAGINATOR_NAME, default_builder

dp = Dispatcher()


@dp.message(CommandStart())
async def get_paginator(message: Message) -> None:
    kb = InlineKeyboardBuilder()

    # Here we create a button, that will start our process of pagination.
    # Be aware, if you want to create pagination for specific users you should replace `user_id` of initial message
    kb.button(
        text="Hey! Get a paginator",
        callback_data=INITIAL_MESSAGE.with_replaced_user_id(
            message.from_user.id
        ).into_callback_data(),
    )
    await message.answer(
        f"Hello, {message.from_user.full_name}! Get a paginator!",
        reply_markup=kb.as_markup(),
    )


# here we create a handler, which reacts only to callback's which look like our paginator
@dp.callback_query(F.data.startswith(PAGINATOR_NAME))
async def paginating(callback_query: CallbackQuery) -> None:
    # let's take our pagination message from callback data and parse it into Python's struct
    asked = INITIAL_MESSAGE.from_callback_data(callback_query.data)

    # and... tha's it! our pagination is ready
    # there is only one task left: we have to send it to user
    # don't forget to specify the builder and fetcher, as other needed params
    # NOTE: there are another params, like text when there are no pages fetched at all,
    # keyboard that have to be sent with this message
    # time-to-live for keyboard to be alive and clickable without refetching
    # and even a language code of your user: it will be used for i18n in keyboards and empty pagebook text
    await paginator.send_paginated(
        callback_query.bot,
        chat_id=callback_query.message.chat.id,
        asked=asked,
        fetcher_iter=fetcher(),
        builder=default_builder,
    )

    await callback_query.answer()


async def main() -> None:
    bot = Bot(
        token=os.getenv("TOKEN"),
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
