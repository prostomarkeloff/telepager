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
from telegrinder.rules import StartCommand, CallbackQueryRule

from filtered import (
    paginator,
    INITIAL_MESSAGE,
    filtering_fetcher,
    default_page_builder,
    PAGINATOR_NAME,
)

api = API(token=Token.from_env())
bot = Telegrinder(api)
logger.set_level("DEBUG")


class CallbackQueryStartswith(CallbackQueryRule):
    def __init__(self, from_: str) -> None:
        self.from_ = from_

    async def check(self, event: CallbackQuery) -> bool:
        data = event.data.unwrap_or_none()
        if not data:
            return False

        return data.startswith(self.from_)


@bot.on.message(StartCommand())
async def get_paginator(message: Message):
    kb = InlineKeyboard()
    kb.add(
        InlineButton(
            text="Hey! Get a paginator",
            callback_data=INITIAL_MESSAGE.with_replaced_user_id(
                message.from_user.id
            ).into_callback_data(),
        )
    )

    await message.reply("Hi!, get a paginator!", reply_markup=kb.get_markup())


@bot.on.callback_query(CallbackQueryStartswith(PAGINATOR_NAME))
async def pagination(callback_query: CallbackQuery):
    asked = INITIAL_MESSAGE.from_callback_data(callback_query.data.unwrap())

    await paginator.send_paginated(
        callback_query.ctx_api,
        chat_id=callback_query.chat_id.unwrap(),
        asked=asked,
        fetcher_iter=filtering_fetcher(),
        builder=default_page_builder,
    )

    await callback_query.answer()


bot.run_forever(skip_updates=True)
