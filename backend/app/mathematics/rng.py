from __future__ import annotations

from collections.abc import Generator

_MASK = 0xFFFFFFFF


def create_rng(seed: int) -> Generator[float, None, None]:
    """Mulberry32 PRNG — Python port of the TypeScript implementation.

    Applies a 32-bit mask after each arithmetic step to mirror JavaScript's
    unsigned 32-bit integer behaviour.
    """
    s = seed & _MASK
    while True:
        s = (s + 0x6D2B79F5) & _MASK
        z = s
        z = (((z ^ (z >> 15)) & _MASK) * ((z | 1) & _MASK)) & _MASK
        z = (z ^ (z + (((z ^ (z >> 7)) & _MASK) * ((z | 61) & _MASK)) & _MASK)) & _MASK
        z = (z ^ (z >> 14)) & _MASK
        yield z / 0x100000000
