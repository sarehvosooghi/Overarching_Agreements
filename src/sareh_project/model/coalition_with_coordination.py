"""
coalition_with_coordination.py
================================
Computes the equilibrium coalition structure when overarching (coordinated)
agreements are allowed, under separation of power (technocrats set abatement)
with a quadratic cost function.

Public API
----------
compute_coalition_with_coordination()
    Called with no arguments by task_01.  Reads all parameters from
    constants.py and returns a dict with, for each of the two horizons
    (T = TP and T = TimeRange):

        "cs_star"  : list of lists — equilibrium coalition sizes for n=1..N
        "vt_small" : list of floats — loss of the smallest-coalition member
        "vt_big"   : list of floats — loss of the largest-coalition member
        "vt_grand" : list of floats — loss if the grand coalition {n} formed
        "z_paths"  : list of arrays — Z_t path (t=0..T_path) under cs_star[n]

    the long-horizon (T = TimeRange) versions of these five objects are
    returned under the same keys suffixed with "_long".

THE BUG THAT WAS FIXED
-----------------------
At every n, the equilibrium continuation structure M*_{n-m1} that forms
alongside a peeling coalition of size m1 CAN legitimately already contain
an overarching sub-block from an earlier step of the recursion (e.g. for
n=10 an overarching {5,5} may already be M*_10; then at n=11, m1=1 peels
off as a singleton and the remaining 10 countries keep {5,5}, giving
{5,5,1}). Overarching agreements are checked at every n, not only at the
top, n=N — the negotiating room can shrink to any size n<N during the
sequential bargaining process, and an overarching agreement can be
proposed to whichever n countries are active in the room at that point.

The bug was in how a candidate for n was ASSEMBLED, not in when
overarching was checked. The previous version built peeling candidates as
equil[n-r] + equil[r] for various split sizes r — i.e., it combined TWO
already-computed equilibrium structures. Since each of equil[n-r] and
equil[r] can itself already contain an overarching sub-block, splicing two
of them together can produce a structure with TWO independent overarching
blocks (e.g. {4,4} from one piece and {2,2} from the other, giving the
invalid {4,4,2,2} at N=12). This violates two things at once: (i) an
overarching agreement, by Definition 1, must include ALL countries present
in the negotiation room at the time it forms, so a structure can contain
AT MOST ONE overarching agreement; and (ii) the peeling coalition m1 must
be a single, freshly-proposed, independent coalition (a genuine one-shot
proposal to m1-1 respondents) — it cannot itself be, or be drawn from
inside, an already-formed overarching agreement.

Fix: build every peeling candidate as a single fresh coalition of size m
(m = 1,...,n-1) combined with the ALREADY-recursively-computed
continuation equil[n-m] — never by combining two recursively-computed
structures. By induction, equil[n-m] contains at most one overarching
block (the base case n=1 trivially contains none), and appending one fresh
independent m-block never introduces a second one, so equil[n] always
satisfies the at-most-one-overarching-agreement requirement, and m1 is
always an independent coalition rather than a fragment carved out of a
previously-formed overarching agreement.
"""

from __future__ import annotations
import numpy as np
from . import constants as C
from .simulation import run_simulation, simulate_Z_path
from .coalition_without_coordination import _build_M


def _proper_factors(n: int) -> list[int]:
    """Divisors k of n with 1 < k < n (so that n/k is a proper sub-coalition)."""
    return [k for k in range(2, n) if n % k == 0]


def _compute_equilibrium(N: int, T: int, tie_tol: float = 1e-8) -> dict[int, tuple[int, ...]]:
    """
    Backward-recursive equilibrium for n = 1,...,N, WITH overarching
    agreements allowed at every step n (not only at n = N).

    At every n, three kinds of candidates are compared:
      (a) the grand coalition {n};
      (b) for every m = 1,...,n-1 such that m is no larger than the
          smallest block already present in equil[n-m]: a single,
          freshly-proposed, independent coalition of size m, peeled off,
          with the remaining n-m countries keeping their own
          recursively-optimal continuation equil[n-m] (which may already
          contain an overarching sub-block). The restriction m <=
          min(equil[n-m]) is what makes m genuinely THE smallest coalition
          of the resulting structure: by sequential rationality (Lemma 2 /
          Ray and Vohra, 2001), the smallest workable coalition is always
          the one with the strongest incentive to peel off first, so a
          larger block can never rationally leave before a smaller one
          that will eventually form within the residual — without this
          restriction, spurious candidates such as {3,1} for n=4 (where a
          monolithic 3-block is forced to leave first even though its
          members would rather fragment further) can numerically look
          attractive and crowd out the true equilibrium;
      (c) for every proper divisor k of n (1<k<n) such that the
          sub-coalition of size n/k is NOT itself an equilibrium of an
          independent subgame of n/k countries: the overarching agreement
          {(n/k)^k}, covering all n countries currently in the room.
    Whichever candidate minimises the loss of a member of its smallest
    block is the equilibrium (ties broken in favour of the coarser, i.e.
    larger-maximum-block, structure).
    """
    equil: dict[int, tuple[int, ...]] = {1: (1,)}

    for n in range(2, N + 1):
        candidates: list[list[int]] = []

        # (a) grand coalition
        candidates.append([n])

        # (b) peel a single independent coalition of size m, keep the
        #     recursively-optimal continuation for the rest -- only when m
        #     is genuinely the smallest block of the resulting structure
        for m in range(1, n):
            residual = equil[n - m]
            if m <= min(residual):
                candidates.append([m] + list(residual))

        # (c) overarching agreement covering all n active countries, only
        #     when the sub-coalition n/k would NOT form independently
        for k in _proper_factors(n):
            sub = n // k
            if equil[sub] != (sub,):
                candidates.append([sub] * k)

        best = None
        best_loss = None
        for parts in candidates:
            M = _build_M(parts)
            V = run_simulation(M, horizon=T)
            final = V[-1]
            sizes = M[:, 0].astype(int).tolist()
            m_min = min(sizes)
            loss_small = float(final[sizes.index(m_min)])

            if best is None or loss_small < best_loss - tie_tol:
                best, best_loss = parts, loss_small
            elif abs(loss_small - best_loss) <= tie_tol and max(parts) > max(best):
                # tie-break: prefer the coarser (larger max block) structure
                best, best_loss = parts, loss_small

        equil[n] = tuple(sorted(best, reverse=True))

    return equil


def solve(N_max: int | None = None, horizon: int | None = None, T_path: int = 200) -> dict[str, object]:
    """
    Equilibrium for n = 1,...,N_max WITH the possibility of overarching
    agreements, at a single horizon T.
    """
    Nmax = int(N_max if N_max is not None else C.N)
    T = int(horizon if horizon is not None else (C.TP if C.TP is not None else C.TimeRange))

    equil = _compute_equilibrium(Nmax, T)

    vt_small = np.zeros(Nmax)
    vt_big   = np.zeros(Nmax)
    vt_grand = np.zeros(Nmax)
    cs_star: list[list[int]] = [None] * Nmax
    z_paths: list[np.ndarray] = [None] * Nmax

    for N in range(1, Nmax + 1):
        cs = list(equil[N])
        M = _build_M(cs)
        V = run_simulation(M, horizon=T)
        final = V[-1]
        sizes = M[:, 0].astype(int).tolist()
        m_min, m_max = min(sizes), max(sizes)

        cs_star[N - 1]  = cs
        vt_small[N - 1] = float(final[sizes.index(m_min)])
        vt_big[N - 1]   = float(final[sizes.index(m_max)])
        vt_grand[N - 1] = float(run_simulation(_build_M([N]), horizon=T)[-1][0])
        z_paths[N - 1]  = simulate_Z_path(M, T_path=T_path)

    return {
        "vt_small": vt_small,
        "vt_big":   vt_big,
        "vt_grand": vt_grand,
        "cs_star":  cs_star,
        "z_paths":  z_paths,
    }


def compute_coalition_with_coordination() -> dict[str, object]:
    """
    Solve the equilibrium with overarching agreements for both time horizons
    defined in constants.py (T = TP, short/myopic column of Table B.1, and
    T = TimeRange, long column).

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
