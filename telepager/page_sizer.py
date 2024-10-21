import typing
from .structs import Line


def counting_page_sizer[T](
    lines: list[Line[T]], page_size: int
) -> typing.Iterator[list[Line[T]]]:
    buffer: list[Line[T]] = []
    for line in lines:
        if len(buffer) == page_size:
            cpy = buffer.copy()
            yield cpy
            buffer.clear()

        buffer.append(line)

    if buffer:
        yield buffer
