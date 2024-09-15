# Telepager

A fancy paginator for your Telegram bots.

Telepager offers to its users a huge bundle of tools out-of-the box, they are: incremental fetching, built-in filtering and sorting support, rich possibilities for page building and so on.

Telepager works both with [telegrinder](https://github.com/timoniq/telegrinder) and [aiogram](https://github.com/aiogram/aiogram)


WIP.
(Documentation is going to be written)


```python
from telepager import (
    Paginator,
    PaginationMessage,
    PaginatorSettings,
    Line,
    NaivePageBuilder,
)

async def fetcher():
    for i in range(1, 10000):
        yield Line(text=str(i), quality=0, meta=None)


paginator = Paginator(
    settings=PaginatorSettings(framework="aiogram", incremental_fetching=True)
)
initial_message = PaginationMessage(name="pagination", user_id=0, recreate_record=True)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Get a paginator", callback_data=initial_message.into_callback_data()
    )
    await message.answer(
        f"Hello, {html.bold(message.from_user.full_name)}! Get a paginator!",
        reply_markup=kb.as_markup(),
    )


@dp.callback_query(F.data.startswith("pagination"))
async def echo_handler(callback_query: CallbackQuery) -> None:
    await paginator.send_paginated(
        callback_query.bot,
        chat_id=callback_query.message.chat.id,
        asked=PaginationMessage.from_callback_data(callback_query.data),
        fetcher_iter=fetcher(),
        builder=NaivePageBuilder("result is: "),
    )
```
