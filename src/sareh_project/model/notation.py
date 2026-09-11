# notation.py
#
# Formats a coalition structure (e.g. [1, 1, 1, 1]) using the paper's
# superscript notation for repeated block sizes (e.g. "1^4"), matching
# Table B.1. A structure with no repeated block size (e.g. [4, 2, 1]) is
# printed as "4,2,1".

from __future__ import annotations
from collections import Counter


def format_structure(parts) -> str:
    counts = Counter(int(p) for p in parts)
    pieces = []
    for size in sorted(counts, reverse=True):
        cnt = counts[size]
        pieces.append(f"{size}^{cnt}" if cnt > 1 else f"{size}")
    return ",".join(pieces)
