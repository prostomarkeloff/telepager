import datetime
import abc
from .structs import Record

type UserId = int
type RecordId = int


class ABCExpiringStorage[T](abc.ABC):
    @abc.abstractmethod
    def put(self, record: Record[T]): ...

    @abc.abstractmethod
    def get_all_records_of_user(self, owner_id: int) -> dict[RecordId, Record[T]]: ...

    @abc.abstractmethod
    def get_record(self, owner_id: int, record_id: int) -> Record[T] | None: ...


class InMemoryExpiringStorage[T](ABCExpiringStorage[T]):
    def __init__(self) -> None:
        self._inner: dict[UserId, dict[RecordId, Record[T]]] = {}

    def put(self, record: Record[T]):
        if not record.owner_id in self._inner:
            self._inner[record.owner_id] = {}
        self._inner[record.owner_id][record.record_id] = record

    def get_all_records_of_user(self, owner_id: int) -> dict[RecordId, Record[T]]:
        return self._inner.setdefault(owner_id, {})

    def get_record(self, owner_id: int, record_id: int) -> Record[T] | None:
        if owner_id not in self._inner:
            return

        record = self._inner[owner_id].get(record_id)
        if not record:
            return
        is_expired = datetime.datetime.now() >= record.expiration_date
        if is_expired:
            del self._inner[owner_id][record_id]
            return

        return record
