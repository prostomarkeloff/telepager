import typing
import enum
import abc

type LANG_CODE = str
type I18N_Text = str | typing.Callable[[LANG_CODE], str]
DEFAULT_LANG_CODE = "ru"  # so i am


def internationalize(text: I18N_Text, language_code: LANG_CODE) -> str:
    if isinstance(text, str):
        return text
    return text(language_code)


class PossibleTexts(enum.Enum):
    ORDERING = enum.auto()
    QUALITIES = enum.auto()
    ALL_QUALITIES = enum.auto()


class ABCI18N(abc.ABC):
    @abc.abstractmethod
    def get_for(self, language_code: LANG_CODE, needed: PossibleTexts) -> str: ...


_default_i18n = {
    PossibleTexts.ORDERING: {"ru": "Сортировка", "en": "Ordering"},
    PossibleTexts.QUALITIES: {"ru": "Фильтры", "en": "Filters"},
    PossibleTexts.ALL_QUALITIES: {"ru": "Все", "en": "All"},
}


class DefaultI18N(ABCI18N):
    def get_for(self, language_code: LANG_CODE, needed: PossibleTexts) -> str:
        return _default_i18n[needed][language_code]
