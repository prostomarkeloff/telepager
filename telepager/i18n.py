import enum
import typing

type LANG_CODE = str
type I18N_Text = str | typing.Callable[[LANG_CODE], str]
DEFAULT_LANG_CODE = "en"


def internationalize(text: I18N_Text, language_code: LANG_CODE) -> str:
    if isinstance(text, str):
        return text
    return text(language_code)


class PossibleTexts(enum.Enum):
    ORDERING = enum.auto()
    QUALITIES = enum.auto()
    ALL_QUALITIES = enum.auto()


DEFAULT_I18N = {
    PossibleTexts.ORDERING: {"ru": "Сортировка", "en": "Ordering", "es": "Ordenar"},
    PossibleTexts.QUALITIES: {"ru": "Фильтры", "en": "Filters", "es": "Filtros"},
    PossibleTexts.ALL_QUALITIES: {"ru": "Все", "en": "All", "es": "Todos"},
}

type PaginatorInternalI18N = dict[PossibleTexts, dict[LANG_CODE, str]]
