"""
Here is the example of paginator with filtering and ordering
"""

import typing
from telepager.flag import Quality, Ordering
from telepager import (
    Paginator,
    PaginatorSettings,
    NaivePageBuilder,
    FetcherIter,
    Line,
)

type MetaT = (
    int  # for our current example the `meta` will be just a number. needed for ordering
)


async def filtering_fetcher() -> FetcherIter[MetaT]:
    for i in range(1, 10000):
        qual: int
        if i % 2 == 0:
            qual = Filters.EVEN
        else:
            qual = Filters.UNEVEN
        yield Line(text=str(i), quality=qual, meta=i)


# filtering in telepager is presented via the concept of `qualities`:
# some properties that lines have and thus can be filtered with.
# qualities are plain enum.IntFlag with the support for correct text rendering
# due to telepager internal mechanisms, your qualities should start with 2
class Filters(Quality):
    EVEN = 2
    UNEVEN = 4

    def shown_name(self, language_code: str) -> str:
        # here we should send name of a filter, according to user's language code
        # i won't make a lot, only for English
        match self:
            case self.EVEN:
                return "Even"
            case self.UNEVEN:
                return "Uneven"


# ordering is the same as qualities, though you'll have to write your own page builder to correctly sort data
class Sorting(Ordering):
    FROM_HIGHEST = 2
    FROM_LOWEST = 4

    def shown_name(self, language_code: str) -> str:
        match self:
            case self.FROM_HIGHEST:
                return "From highest numbers to lowest"
            case self.FROM_LOWEST:
                return "From lowest numbers to highers"


# our page builder will support sorting
class SortingPageBuilder(NaivePageBuilder[MetaT]):
    # to support ordering we just have to implement function `order_by`
    # be aware, that this method is not like other in `PageBuilder`
    # it does ordering for all data qualified to be sent to a user

    async def order_by(
        self, lines: list[Line[MetaT]], asked_ordering: int
    ) -> list[Line[MetaT]]:
        ordered_lines = lines.copy()
        if asked_ordering == Sorting.FROM_HIGHEST:
            ordered_lines.sort(key=lambda i: i.meta, reverse=True)
        elif asked_ordering == Sorting.FROM_LOWEST:
            ordered_lines.sort(key=lambda i: i.meta)

        return ordered_lines


# for details about that look at `examples/base.py`
paginator = Paginator[MetaT](
    settings=PaginatorSettings(
        paginator_name="filtered-ordered",
        quality_type=Filters,
        ordering_type=Sorting,
    )
)

default_page_builder = SortingPageBuilder("Result is: ")
