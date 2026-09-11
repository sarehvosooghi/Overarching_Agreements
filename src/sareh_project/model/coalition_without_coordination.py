# coalition_without_coordination.py — with tolerance & deterministic tie-breaks
#
# Pure Ray and Vohra (2001) backward recursion, WITHOUT overarching agreements.
# This is the baseline algorithm: for every n = 1,...,N it compares the grand
# coalition {n} against the best non-grand structure {m1, M*_{n-m1}}, where
# M*_{n-m1} is itself the equilibrium found recursively at the smaller
# subgame n-m1. Overarching agreements are never considered here — this
# module is also reused, unmodified, as the "pure" continuation structure
# inside coalition_with_coordination.py (see the docstring there).

from __future__ import annotations
import numpy as np
from . import constants as C
from .decomposition import n_decomp
from .simulation import run_simulation, simulate_Z_path

def _build_M(parts: list[int]) -> np.ndarray:
    sizes = sorted(set(parts), reverse=True)
    rows = []
    for m in sizes:
        cnt = parts.count(m)
        rows.append([float(m), float(m * cnt)])  # [size, number of members]
    return np.array(rows, dtype=float)

def _stable_prefix_ok(parts: list[int], cs_star_prefix: list[int] | None) -> bool:
    if len(parts) < 2:
        return True
    if cs_star_prefix is None:
        return True
    return list(parts[:-1]) == list(cs_star_prefix)

def solve(N_max: int | None = None, horizon: int | None = None, T_path: int = 200) -> dict[str, object]:
    """
    Backward-recursive equilibrium for n = 1,...,N_max, ignoring overarching
    agreements (pure Ray and Vohra, 2001).

    Parameters
    ----------
    N_max   : largest number of countries to solve for (defaults to C.N).
    horizon : politicians' evaluation horizon T used to rank structures
              (defaults to C.TP if set, else C.TimeRange). Passed straight
              through to run_simulation() so this function can be called
              at both T = TP (short/myopic) and T = TimeRange (long) to
              reproduce both columns of Table B.1.
    T_path  : length (in periods) of the Z_t path stored for each N's
              equilibrium structure (default 200, per the paper's request
              to report Z_t "up to a long time").
    """
    Nmax = int(N_max if N_max is not None else C.N)
    T = int(horizon if horizon is not None else (C.TP if C.TP is not None else C.TimeRange))
    vt_big   = np.zeros(Nmax)
    vt_small = np.zeros(Nmax)
    vt_grand = np.zeros(Nmax)
    cs_star: list[list[int] | None] = [None] * Nmax
    z_paths: list[np.ndarray] = [None] * Nmax

    TOL = getattr(C, "TIE_TOL", 1e-10)

    # Base N=1
    cs_star[0] = [1]
    V1 = run_simulation(_build_M([1]), horizon=T)
    vt_small[0] = vt_big[0] = vt_grand[0] = float(V1[-1][0])
    z_paths[0] = simulate_Z_path(_build_M([1]), T_path=T_path)

    for N in range(2, Nmax + 1):
        candidates = list(n_decomp(N))
        filtered = []
        for parts in candidates:
            residual = N - parts[-1]
            prev = cs_star[residual - 1] if residual >= 1 else None
            if _stable_prefix_ok(parts, prev):
                filtered.append(parts)

        best_loss = float("inf")
        pool: list[tuple[list[int], np.ndarray]] = []

        for parts in filtered:
            M = _build_M(parts)
            V = run_simulation(M, horizon=T)
            final = V[-1]
            sizes = M[:, 0].astype(int).tolist()
            m_min, m_max = min(sizes), max(sizes)
            loss_small = float(final[sizes.index(m_min)])

            if loss_small < best_loss - TOL:
                best_loss = loss_small
                pool = [(parts, final)]
            elif abs(loss_small - best_loss) <= TOL:
                pool.append((parts, final))

        assert pool, "No candidates after filtering."
        # tie-breaker: prefer the candidate whose smallest block is largest
        def tie_key(item):
            parts, _final = item
            return min(parts)
        parts_best, final_best = max(pool, key=tie_key)
        cs_star[N - 1] = parts_best

        M_best = _build_M(parts_best)
        sizes = M_best[:, 0].astype(int).tolist()
        m_min, m_max = min(sizes), max(sizes)
        vt_small[N - 1] = float(final_best[sizes.index(m_min)])
        vt_big[N - 1]   = float(final_best[sizes.index(m_max)])

        vt_grand[N - 1] = float(run_simulation(_build_M([N]), horizon=T)[-1][0])
        z_paths[N - 1] = simulate_Z_path(M_best, T_path=T_path)

    return {
        "vt_big": vt_big,
        "vt_small": vt_small,
        "vt_grand": vt_grand,
        "cs_star": cs_star,
        "z_paths": z_paths,
    }

# export name used by tasks
def compute_coalition_without_coordination() -> dict[str, object]:
    """
    Solve the pure (no-overarching) equilibrium for both time horizons
    defined in constants.py (T = TP, the short/myopic column of Table B.1,
    and T = TimeRange, the long/near-non-myopic column), mirroring the API
    of compute_coalition_with_coordination() in coalition_with_coordination.py.

    Returns a dict with:
        "vt_small", "vt_big", "vt_grand", "cs_star", "z_paths"
            -> short horizon (T = C.TP)

        "vt_small_long", "vt_big_long", "vt_grand_long", "cs_star_long", "z_paths_long"
            -> long horizon (T = C.TimeRange)
    """
    N = C.N
    T_short = C.TP if C.TP is not None else C.TimeRange

    res_short = solve(N_max=N, horizon=T_short)
    res_long  = solve(N_max=N, horizon=C.TimeRange)

    out = dict(res_short)
    out["vt_small_long"] = res_long["vt_small"]
    out["vt_big_long"]   = res_long["vt_big"]
    out["vt_grand_long"] = res_long["vt_grand"]
    out["cs_star_long"]  = res_long["cs_star"]
    out["z_paths_long"]  = res_long["z_paths"]
    return out
