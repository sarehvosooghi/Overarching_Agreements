# coalition_with_coordination.py — with tolerance & deterministic tie-breaks

from __future__ import annotations
import numpy as np
from . import constants as C
from .decomposition import n_decomp
from .simulation import run_simulation

def _build_M(parts: list[int]) -> np.ndarray:
    sizes = sorted(set(parts), reverse=True)
    rows = []
    for m in sizes:
        cnt = parts.count(m)
        rows.append([float(m), float(m * cnt)])  # [size, number of members]
    return np.array(rows, dtype=float)

def _is_equal_split(parts: list[int]) -> bool:
    return len(parts) >= 2 and all(p == parts[0] for p in parts)

def _stable_prefix_ok(parts: list[int], cs_star_prefix: list[int] | None) -> bool:
    # allow single block always
    if len(parts) < 2:
        return True
    if cs_star_prefix is None:
        return True
    return list(parts[:-1]) == list(cs_star_prefix)

def solve(N_max: int | None = None) -> dict[str, object]:
    Nmax = int(N_max if N_max is not None else C.N)
    vt_big   = np.zeros(Nmax)
    vt_small = np.zeros(Nmax)
    vt_grand = np.zeros(Nmax)
    cs_star: list[list[int] | None] = [None] * Nmax

    TOL = getattr(C, "TIE_TOL", 1e-10)

    # Base N=1
    cs_star[0] = [1]
    V1 = run_simulation(_build_M([1]))
    vt_small[0] = vt_big[0] = vt_grand[0] = float(V1[-1][0])

    for N in range(2, Nmax + 1):
        # 1) Enumerate partitions and inject equal splits
        candidates = set(tuple(p) for p in n_decomp(N))
        for k in range(2, N + 1):
            if N % k == 0:
                parts = tuple([N // k] * k)
                candidates.add(parts)

        # 2) Apply sequential-stability to non-equal-splits only
        filtered = []
        for p in candidates:
            parts = list(p)
            if _is_equal_split(parts):
                filtered.append(parts)
            else:
                residual = N - parts[-1]
                prev = cs_star[residual - 1] if residual >= 1 else None
                if _stable_prefix_ok(parts, prev):
                    filtered.append(parts)

        # 3) Evaluate and choose using tolerance + tie-breaks
        best_loss = float("inf")
        pool: list[tuple[list[int], np.ndarray]] = []

        for parts in filtered:
            M = _build_M(parts)
            V = run_simulation(M)
            final = V[-1]
            sizes = M[:, 0].astype(int).tolist()
            m_min, m_max = min(sizes), max(sizes)
            loss_small = float(final[sizes.index(m_min)])

            if loss_small < best_loss - TOL:
                best_loss = loss_small
                pool = [(parts, final)]
            elif abs(loss_small - best_loss) <= TOL:
                pool.append((parts, final))

        # tie-breaker: prefer the candidate whose smallest block is largest
        assert pool, "No candidates after filtering."
        def tie_key(item):
            parts, _final = item
            return min(parts)
        parts_best, final_best = max(pool, key=tie_key)
        cs_star[N - 1] = parts_best

        # record values for chosen partition
        sizes = _build_M(parts_best)[:, 0].astype(int).tolist()
        m_min, m_max = min(sizes), max(sizes)
        vt_small[N - 1] = float(final_best[sizes.index(m_min)])
        vt_big[N - 1]   = float(final_best[sizes.index(m_max)])

        # grand coalition
        vt_grand[N - 1] = float(run_simulation(_build_M([N]))[-1][0])

    return {"vt_big": vt_big, "vt_small": vt_small, "vt_grand": vt_grand, "cs_star": cs_star}

# export name used by tasks
def compute_coalition_with_coordination(*args, **kwargs):
    return solve(*args, **kwargs)
