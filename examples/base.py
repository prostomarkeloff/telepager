from telepager import (
    ANY_QUALITY,
    FetcherIter,
    Line,
    NaivePageBuilder,
    Paginator,
    PaginatorSettings,
)


# This function generates 10.000 lines, simply containing theirs number and having no quality (no filter)
# also they have no `meta`. Meta variable is some additional information, that can be used by PageBuilder
# for generation of a keyboard for a page or anything else
async def fetcher() -> FetcherIter[None]:
    for i in range(1, 10000):
        yield Line(text=str(i), quality=ANY_QUALITY, meta=None)


# here is presented the default page builder, the thing putting your `Line`s to your Page
# the naive one just gets your text and puts your lines after `\n`
default_builder = NaivePageBuilder[None]("The result is: ")

# here we create our paginator object.
# we have to specify its settings, to make it usable.
# in favor of this example, I have enabled 'incremental_fetcing', the telepager internal's mechanism
# letting it to fetch not all like 10.000 lines, but thousand by thounsand, when the half of it is already seen by user
# you can change the step and fetch not the 1.000, but 2.000 and so on, the paginator is very programmable
# also you can specify default ttl, page builder, even the page sizer (a thing, letting page have its size: a number of lines on it)
# the page sizer is a sophisticated mechanism, that shouldn't be touched without a solid need.
# enjoy looking at PaginatorSettings definition, to get its full list of settings.
paginator = Paginator[None](
    settings=PaginatorSettings(
        paginator_name="our-paginator",
        incremental_fetching=True,
        default_page_builder=default_builder,
    )
)
