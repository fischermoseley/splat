from math import ceil


def words_to_value(data):
    """Takes a list of integers, interprets them as 16-bit integers, and
    concatenates them together in little-endian order."""

    for d in data:
        if d > 0 and d > 2**16 - 1:
            raise ValueError("Unsigned integer too large.")

        if d < 0 and d < -(2**15 - 1):
            raise ValueError("Signed integer too large.")

    return int("".join([f"{i:016b}" for i in data[::-1]]), 2)


def value_to_words(data, n_words):
    """Takes a integer, interprets it as a set of 16-bit integers
    concatenated together, and splits it into a list of 16-bit numbers"""

    if not isinstance(data, int) or data < 0:
        raise ValueError("Behavior is only defined for nonnegative integers.")

    # convert to binary, split into 16-bit chunks, and then convert back to list of int
    binary = f"{data:0b}".zfill(n_words * 16)
    return [int(binary[i : i + 16], 2) for i in range(0, 16 * n_words, 16)][::-1]
