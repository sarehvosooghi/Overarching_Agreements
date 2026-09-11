# coalition_without_coordination_myopic.py
#
# The "without separation of power" counterpart to
# coalition_without_coordination.py. Same pure Ray and Vohra (2001)
# backward recursion (no overarching agreements are ever considered here,
# matching Sections 3-4 of the paper, which precede the introduction of
# overarching agreements in Section 5), the ONLY difference is that the
# politicians here set their OWN abatement, q_hat_i(m,T) -- equation (2.5),
# implemented in simulation_myopic.run_simulation_myopic() -- instead of
# having a technocrat set q*(m) -- equation (4.1) -- for them under
# separation of power.

from __future__ import annotations
import numpy as np
from . import constants as C
from .decomposition import n_decomp
from .simulation_myopic import run_simulation_myopic, simulate_Z_path_myopic
from .coalition_without_coordination import _build_M, _stable_prefix_ok

def solve(N_max: int | None = None, horizon: int | None = None, T_path: int = 200) -> dict[str, object]:
    """
    Backward-recursive equilibrium for n = 1,...,N_max, ignoring overarching
    agreements, WITHOUT separation of power: politicians both choose
    membership and set their own abatement q_hat(m,T), equation (2.5).
    """
    Nmax = int(N_max if N_max is not None else C.N)
    T = int(horizon if horizon is not None else (C.TP if C.TP is not None else C.TimeRange))
    vt_big   = np.zeros(Nmax)
    vt_small = np.zeros(Nmax)
    vt_grand = np.zeros(Nmax)
    cs_star: list[list[int] | None] = [None] * Nmax
    z_paths: list[np.ndarray] = [None] * Nmax

    TOL = getattr(C, "TIE_TOL", 1e-10)

    cs_star[0] = [1]
    V1 = run_simulation_myopic(_build_M([1]), horizon=T)
    vt_small[0] = vt_big[0] = vt_grand[0] = float(V1[-1][0])
    z_paths[0] = simulate_Z_path_myopic(_build_M([1]), horizon=T, T_path=T_path)

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
            V = run_simulation_myopic(M, horizon=T)
            final = V[-1]
            sizes = M[:, 0].astype(int).tolist()
            m_min = min(sizes)
            loss_small = float(final[sizes.index(m_min)])

            if loss_small < best_loss - TOL:
                best_loss = loss_small
                pool = [(parts, final)]
            elif abs(loss_small - best_loss) <= TOL:
                pool.append((parts, final))

        assert pool, "No candidates after filtering."
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

        vt_grand[N - 1] = float(run_simulation_myopic(_build_M([N]), horizon=T)[-1][0])
        z_paths[N - 1] = simulate_Z_path_myopic(M_best, horizon=T, T_path=T_path)

    return {
        "vt_big": vt_big,
        "vt_small": vt_small,
        "vt_grand": vt_grand,
        "cs_star": cs_star,
        "z_paths": z_paths,
    }

def compute_coalition_without_separation_of_power(T_low: int, T_high: int) -> dict[str, object]:
    """
    Solve the pure (no-overarching), no-separation-of-power equilibrium at
    two horizons T_low (short) and T_high (long).

    Returns a dict with:
        "cs_star", "vt_small", "vt_big", "vt_grand", "z_paths"       -> T = T_low
        "cs_star_long", "vt_small_long", ..., "z_paths_long"         -> T = T_high
    """
    N = C.N
    res_low  = solve(N_max=N, horizon=T_low)
    res_high = solve(N_max=N, horizon=T_high)

    out = dict(res_low)
    out["vt_small_long"] = res_high["vt_small"]
    out["vt_big_long"]   = res_high["vt_big"]
    out["vt_grand_long"] = res_high["vt_grand"]
    out["cs_star_long"]  = res_high["cs_star"]
    out["z_paths_long"]  = res_high["z_paths"]
    return out
