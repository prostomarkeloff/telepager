"""
Here we put our funcs and vals needed only for paginating reasons
"""

from telepager import (
    Paginator,
    PaginationMessage,
    PaginatorSettings,
    Line,
    FetcherIter,
    NaivePageBuilder,
    ANY_QUALITY,
)


# This function generates 10.000 lines, simply containing theirs number and having no quality (no filter)
# also they have no `meta`. Meta variable is some additional information, that can be used by PageBuilder
# for generation a keyboard for a page or anything else
async def fetcher() -> FetcherIter[None]:
    for i in range(1, 10000):
        yield Line(text=str(i), quality=ANY_QUALITY, meta=None)

# here we create our paginatior object. in place of `framework` we should put the name of our telegram's bot library
# by default it considers it to be `telegrinder`, but in favor of our aiogram example here it would be `aiogram`
# also, telepager offers us an ability to fetch data incrementally (maybe, your fetcher goes to net to get data; it can be slow sometimes)
# but by default it's disabled; for sake of showing you that telepager is able to do it - I'll enable it.
paginator = Paginator[None](
    settings=PaginatorSettings(paginator_name="our-paginator", incremental_fetching=True)
)

# here is presented the default page builder, the thing putting your `Line`s to your Page
# the naive one just gets your text and puts your lines after `\n`
default_builder = NaivePageBuilder[None]("The result is: ")
