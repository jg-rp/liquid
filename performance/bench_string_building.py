from io import StringIO
from timeit import repeat


def build_list(chunks: list[str]) -> str:
    parts: list[str] = []
    for chunk in chunks:
        parts.append(chunk)
    return "".join(parts)


def build_stringio(chunks: list[str]) -> str:
    out = StringIO()
    for chunk in chunks:
        out.write(chunk)
    return out.getvalue()


def benchmark(
    total_chars: int = 50_000,
    chunk_size: int = 20,
    repeats: int = 7,
    number: int = 1_000,
):
    # Pre-build the input so we're measuring string accumulation,
    # not the cost of generating the strings.
    chunk = "x" * chunk_size
    chunks = [chunk] * (total_chars // chunk_size)

    # Make sure both implementations produce exactly the same result.
    assert build_list(chunks) == build_stringio(chunks)

    list_times = repeat(
        lambda: build_list(chunks),
        repeat=repeats,
        number=number,
    )

    stringio_times = repeat(
        lambda: build_stringio(chunks),
        repeat=repeats,
        number=number,
    )

    list_best = min(list_times) / number
    stringio_best = min(stringio_times) / number

    print(f"\n{total_chars:,} chars, {chunk_size}-char writes")
    print(f"list + join : {list_best * 1e6:8.2f} µs")
    print(f"StringIO    : {stringio_best * 1e6:8.2f} µs")
    print(f"ratio       : {stringio_best / list_best:8.2f}x")


if __name__ == "__main__":
    for total_chars in (10_000, 50_000, 100_000, 1_000_000):
        benchmark(total_chars=total_chars, chunk_size=20)
