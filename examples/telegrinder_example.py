from telegrinder import (
    API,
    Message,
    CallbackQuery,
    Telegrinder,
    Token,
    InlineKeyboard,
    InlineButton,
)
from telegrinder.modules import logger
from telegrinder.rules import StartCommand
from telepager import PaginationMessage
from telepager import TelepagerMessage, setup_empty_callback_data_handler

from .filtered import (
    paginator,
    filtering_fetcher,
    default_page_builder,
)

api = API(token=Token.from_env())
bot = Telegrinder(api)
logger.set_level("INFO")
setup_empty_callback_data_handler(paginator, bot.dispatch)


@bot.on.message(StartCommand())
async def get_paginator(message: Message):
    kb = InlineKeyboard()
    kb.add(
        InlineButton(
            text="Hey! Get a paginator",
            callback_data=paginator.initial_message.for_user(message.from_user.id),
            callback_data_serializer=paginator.settings.serializer,
        )
    )
    await message.reply("Hi!, get a paginator!", reply_markup=kb.get_markup())


@bot.on.callback_query(TelepagerMessage(paginator, alias="asked"))
async def pagination(
    callback_query: CallbackQuery,
    asked: PaginationMessage,
):
    await paginator.send_paginated(
        callback_query.ctx_api,
        chat_id=callback_query.chat_id.unwrap(),
        asked=asked,
        fetcher_iter=filtering_fetcher(),
        builder=default_page_builder,
    )

    await callback_query.answer()


bot.run_forever(skip_updates=True)
