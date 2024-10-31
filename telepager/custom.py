import typing
from fntypes import Error, Ok
from telegrinder import CallbackQuery, Context, Dispatch
from telegrinder.rules import PayloadEqRule, CallbackQueryDataRule

if typing.TYPE_CHECKING:
    from telepager import Paginator


class TelepagerMessage[T](CallbackQueryDataRule):
    def __init__(
        self,
        paginator: "Paginator[T]",
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


def setup_empty_callback_data_handler[T](paginator: "Paginator[T]", dp: Dispatch):
    @dp.callback_query(PayloadEqRule(paginator.settings.empty_callback_data))
    async def _(query: CallbackQuery):
        await query.answer()
