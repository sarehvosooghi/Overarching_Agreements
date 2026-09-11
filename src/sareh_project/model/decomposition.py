# decomposition.py — lean

from __future__ import annotations

def n_decomp(n: int) -> list[tuple[int, ...]]:
    """All integer partitions of n in nonincreasing order (as tuples)."""
    out: list[tuple[int, ...]] = []
    def rec(rem: int, max_part: int, pref: list[int]) -> None:
        if rem == 0:
            out.append(tuple(pref))
            return
        for m in range(min(rem, max_part), 1 - 1, -1):
            pref.append(m)
            rec(rem - m, m, pref)
            pref.pop()
    rec(n, n, [])
    return out
