import dataclasses
import datetime
import functools
import typing

from telegrinder.tools import ABCDataSerializer, MsgPackSerializer

from .flag import FLAG_T
from .i18n import DEFAULT_I18N, I18N_Text, PaginatorInternalI18N
from .page_sizer import counting_page_sizer
from .structs import DefaultFactory, FetcherIter, PageSizerFactory, PaginationMessage
from .custom import TelepagerSerializer

if typing.TYPE_CHECKING:
    from .manager import ABCPageBuilder

FOREVER = datetime.timedelta(days=10000)  # sure bot gets reload


@dataclasses.dataclass
class PaginatorSettings[T]:
    paginator_name: str
    initial_message: PaginationMessage = dataclasses.field(init=False)

    page_size: dataclasses.InitVar[int] = 20
    page_sizer_factory: PageSizerFactory[T] | None = None
    incremental_fetching_step: int = 1000  # 1000 lines
    serializer: ABCDataSerializer[PaginationMessage] = TelepagerSerializer()
    i18n: PaginatorInternalI18N = dataclasses.field(
        default_factory=lambda: DEFAULT_I18N
    )
    empty_callback_data: str = "__telepager_empty__"  # callback data for touching buttons that are not interactive
    incremental_fetching: bool = False
    quality_type: FLAG_T | None = None
    ordering_type: FLAG_T | None = None

    default_page_builder: "ABCPageBuilder[T] | None" = None
    default_fetcher_factory: DefaultFactory[FetcherIter[T]] | None = None
    default_language_code: str = "en"
    default_empty_page_book_text: I18N_Text | None = None
    default_ttl: datetime.timedelta = FOREVER

    def __post_init__(self, page_size: int):
        self.initial_message = PaginationMessage(
            name=self.paginator_name,
        )
        if not self.page_sizer_factory:
            self.page_sizer_factory = lambda: functools.partial(
                counting_page_sizer, page_size=page_size
            )
