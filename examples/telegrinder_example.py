from telegrinder import (
    API,
    CallbackQuery,
    InlineButton,
    InlineKeyboard,
    Message,
    Telegrinder,
    Token,
)
from telegrinder.modules import logger
from telegrinder.rules import StartCommand

from telepager import (
    PaginationMessage,
    TelepagerMessage,
    setup_empty_callback_data_handler,
)

from .filtered import paginator

api = API(token=Token.from_env())
bot = Telegrinder(api)
logger.set_level("DEBUG")

# some buttons are not touchable. let telepager handle them with simple `callback_query.answer()`
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
    await paginator.send_paginated(callback_query, asked)

    await callback_query.answer()


bot.run_forever(skip_updates=True)
