from fntypes import Ok, Error
from telepager import Paginator
from telegrinder.rules import CallbackQueryDataRule, CallbackDataEq
from telegrinder import CallbackQuery, Context, Dispatch


class TelepagerMessage[T](CallbackQueryDataRule):
    def __init__(
        self,
        paginator: Paginator[T],
        *,
        alias: str = "pagination_message",
    ) -> None:
        self.alias = alias
        self.paginator = paginator

    def check(self, event: CallbackQuery, ctx: Context) -> bool:
        match self.paginator.settings.serializer.deserialize(event.data.unwrap()):
            case Ok(data):
                if data.name != self.paginator.settings.paginator_name:
                    return False
                ctx.set(self.alias, data)
                return True
            case Error(_):
                return False


def setup_empty_callback_data_handler[T](paginator: Paginator[T], dp: Dispatch):
    @dp.callback_query(CallbackDataEq(paginator.settings.empty_callback_data))
    async def _(query: CallbackQuery):
        await query.answer()
