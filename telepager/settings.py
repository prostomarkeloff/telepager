import dataclasses
import functools
from telegrinder.tools import (
    ABCDataSerializer,
    MsgPackSerializer,
)

from telepager.structs import PaginationMessage

from .i18n import DEFAULT_I18N, PaginatorInternalI18N
from .flag import FLAG_T
from .structs import PageSizerFactory
from .page_sizer import counting_page_sizer


@dataclasses.dataclass
class PaginatorSettings[T]:
    paginator_name: str
    initial_message: PaginationMessage = dataclasses.field(init=False)

    page_size: dataclasses.InitVar[int] = 20
    page_sizer_factory: PageSizerFactory[T] | None = None
    incremental_fetching_step: int = 1000  # 1000 lines
    serializer: ABCDataSerializer[PaginationMessage] = MsgPackSerializer(
        PaginationMessage
    )
    i18n: PaginatorInternalI18N = dataclasses.field(
        default_factory=lambda: DEFAULT_I18N
    )
    empty_callback_data: str = "__telepager_empty__"  # callback data for touching buttons that are not interactive
    incremental_fetching: bool = False
    quality_type: FLAG_T | None = None
    ordering_type: FLAG_T | None = None

    def __post_init__(self, page_size: int):
        self.initial_message = PaginationMessage(
            name=self.paginator_name,
        )
        if not self.page_sizer_factory:
            self.page_sizer_factory = lambda: functools.partial(
                counting_page_sizer, page_size=page_size
            )
