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

PAGINATOR_NAME = "our-paginator"

# here we create our paginatior object. in place of `framework` we should put the name of our telegram's bot library
# by default it considers it to be `telegrinder`, but in favor of our aiogram example here it would be `aiogram`
# also, telepager offers us an ability to fetch data incrementally (maybe, your fetcher goes to net to get data; it can be slow sometimes)
# but by default it's disabled; for sake of showing you that telepager is able to do it - I'll enable it.
paginator = Paginator[None](
    settings=PaginatorSettings(framework="aiogram", incremental_fetching=True)
)
# telepager communicates its parts via `PaginationMessage`
# to begin the process of paginating we should send this to user
# NOTE: please be aware that name should look like `this-is-name`, not `this_is_name`
# the `user_id` is set to 0 here, but we will change it in handler to appropriate
# the `recreate_record` is a signal to paginator that we want to drop the current user's state of paginating
# and refetch the data, putting user at start. It should be `True` when we even haven't created the user
INITIAL_MESSAGE = PaginationMessage(
    name=PAGINATOR_NAME, user_id=0, recreate_record=True
)

# here is presented the default page builder, the thing putting your `Line`s to your Page
# the naive one just gets your text and puts your lines after `\n`
default_builder = NaivePageBuilder[None]("The result is: ")
