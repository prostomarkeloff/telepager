import typing
from fntypes import Error, Ok, Result
from telegrinder import CallbackQuery, Context, Dispatch
from telegrinder.rules import PayloadEqRule, CallbackQueryDataRule
from telegrinder.tools.callback_data_serilization import ABCDataSerializer

if typing.TYPE_CHECKING:
    from telepager import Paginator
    from telepager import PaginationMessage


def parse_callback_data(inp: str) -> tuple[str, list[str]]:
    parts = inp.split("_")
    name = parts[0]
    args: list[str]
    try:
        args = parts[1:]
    except IndexError:
        args = []
    return name, args


class TelepagerSerializer(ABCDataSerializer["PaginationMessage"]):
    def __init__(self) -> None:
        self.ident_key = "tpgr"

    def serialize(self, data: "PaginationMessage") -> str:
        return f"{data.name}_{data.user_id}_{data.record_id}_{data.page}_{data.quality}_{data.ordering}_{int(data.show_all_filters)}_{int(data.show_all_ordering)}"

    def deserialize(self, serialized_data: str) -> Result["PaginationMessage", str]:
        from telepager import PaginationMessage

        name, args = parse_callback_data(serialized_data)
        if len(args) != 7:
            return Error("That's not a pagination message")
        user_id = int(args[0])
        record_id = int(args[1])
        page = int(args[2])
        quality = int(args[3])
        ordering = int(args[4])
        show_all_filters = bool(int(args[5]))
        show_all_ordering = bool(int(args[6]))

        return Ok(PaginationMessage(
            name,
            user_id,
            record_id,
            page,
            quality,
            ordering,
            show_all_filters,
            show_all_ordering,
        ))


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
