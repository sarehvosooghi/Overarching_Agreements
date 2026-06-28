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
    constants.py and returns a dict with four lists, each of length N:

        "cs_star"  : list of lists — equilibrium coalition sizes for n=1..N
        "vt_small" : list of floats — loss of the smallest-coalition member
        "vt_big"   : list of floats — loss of the largest-coalition member
        "vt_grand" : list of floats — loss if the grand coalition {n} formed

    Two horizons are computed (T=TP and T=TimeRange); the dict contains
    both under the keys shown above suffixed with "_short" and "_long",
    PLUS the short-horizon values as the bare keys (for backward compat).

THE BUG THAT WAS FIXED
-----------------------
The old code filtered candidates by peeling off the last single element of
a partition and checking the prefix against the stored equilibrium of the
residual.  For n=12 this rejected [4,4,2,2] because the prefix [4,4,2]
did not match equil[10]=[4,4,1,1].

Fix: build every candidate as  equil[n-r] + equil[r]  for r = 1..n//2.
This correctly picks up [4,4]+[2,2] at n=12 via r=4.
"""

import sareh_project.model.constants as C


# ────────────────────────────────────────────────────────────────────────────
# Loss-function building blocks
# (quadratic cost, separation of power → technocrat abatement q*(m))
# ────────────────────────────────────────────────────────────────────────────

def _B1(T, beta):
    return (1.0 - beta ** T) / (1.0 - beta)


def _B2(T, beta, eta, phi):
    if T <= 1:
        return 0.0
    return (beta * eta / (1.0 - phi)) * (
        (1.0 - beta ** (T - 1)) / (1.0 - beta)
        - phi * (1.0 - (beta * phi) ** (T - 1)) / (1.0 - beta * phi)
    )


def _B3(T, beta, eta, phi):
    return eta * (1.0 - (beta * phi) ** T) / (1.0 - beta * phi)


def _q_star(m, beta, eta, phi):
    """Technocrat abatement per member for a coalition of size m."""
    return m * beta * eta / (1.0 - beta * phi)


def _member_loss(m, full_struct, T, beta, eta, phi, psi, Z0):
    """
    Discounted loss for one member of a coalition of size m,
    given the complete coalition structure full_struct.
    """
    q_me = _q_star(m, beta, eta, phi)
    total_q = sum(s * _q_star(s, beta, eta, phi) for s in full_struct)
    return (
        _B1(T, beta) * (q_me ** 2 / 2.0)
        + _B2(T, beta, eta, phi) * (psi - total_q)
        + _B3(T, beta, eta, phi) * Z0
    )


# ────────────────────────────────────────────────────────────────────────────
# Helper: proper divisors k of n  with  1 < k < n
# ────────────────────────────────────────────────────────────────────────────

def _proper_factors(n):
    return [k for k in range(2, n) if n % k == 0]


# ────────────────────────────────────────────────────────────────────────────
# Core equilibrium algorithm
# ────────────────────────────────────────────────────────────────────────────

def _compute_equilibrium(N, T, beta, eta, phi, psi, Z0, tie_tol=1e-8):
    """
    Backward-recursive equilibrium for n = 1..N with overarching agreements.

    Returns
    -------
    equil : dict  n -> tuple of coalition sizes (sorted descending)
    """
    equil = {1: (1,)}

    for n in range(2, N + 1):

        candidates = []

        # 1. Grand coalition {n}
        candidates.append([n])

        # 2. All singletons {1^n}
        candidates.append([1] * n)

        # 3. equil[n-r] + equil[r]  for every split r = 1..n//2
        #    *** THIS IS THE KEY FIX ***
        #    Combines previously found equilibria for every valid split size.
        #    e.g. n=12, r=4: equil[8]=[4,4]  +  equil[4]=[2,2]  →  [4,4,2,2]
        for r in range(1, n // 2 + 1):
            nr = n - r
            if r in equil and nr in equil:
                candidates.append(list(equil[nr]) + list(equil[r]))

        # 4. Equal-split overarching {(n/k)^k}
        #    Only when sub-coalition CANNOT form independently
        #    (i.e. equil[sub] ≠ (sub,) — the definition of a true overarching)
        for k in _proper_factors(n):
            sub = n // k
            if sub in equil and equil[sub] != (sub,):
                candidates.append([sub] * k)

        # Select best: minimise smallest-coalition-member loss;
        # tie-break by preferring larger maximum coalition size.
        best = candidates[0]
        best_loss = _member_loss(min(best), best, T, beta, eta, phi, psi, Z0)
        best_max = max(best)

        for struct in candidates[1:]:
            l = _member_loss(min(struct), struct, T, beta, eta, phi, psi, Z0)
            larger = max(struct) > best_max
            if l < best_loss - tie_tol or (abs(l - best_loss) < tie_tol and larger):
                best = struct
                best_loss = l
                best_max = max(struct)

        equil[n] = tuple(sorted(best, reverse=True))

    return equil


# ────────────────────────────────────────────────────────────────────────────
# Build the result dict that task_01 expects
# ────────────────────────────────────────────────────────────────────────────

def _build_result(equil, N, T, beta, eta, phi, psi, Z0):
    """
    Given an equilibrium dict, return the four lists task_01 needs.
    """
    vt_small, vt_big, vt_grand, cs_star = [], [], [], []
    for n in range(1, N + 1):
        cs = list(equil[n])
        vt_small.append(_member_loss(min(cs), cs, T, beta, eta, phi, psi, Z0))
        vt_big.append(_member_loss(max(cs), cs, T, beta, eta, phi, psi, Z0))
        vt_grand.append(_member_loss(n, [n], T, beta, eta, phi, psi, Z0))
        cs_star.append(cs)
    return {
        "vt_small": vt_small,
        "vt_big":   vt_big,
        "vt_grand": vt_grand,
        "cs_star":  cs_star,
    }


# ────────────────────────────────────────────────────────────────────────────
# Public function — called by task_01 with NO arguments
# ────────────────────────────────────────────────────────────────────────────

def compute_coalition_with_coordination():
    """
    Solve the equilibrium with overarching agreements for both time horizons
    defined in constants.py.

    Returns a dict with:
        "vt_small", "vt_big", "vt_grand", "cs_star"
            → short horizon (T = C.TP, e.g. 60)   ← what task_01 uses directly

        "vt_small_long", "vt_big_long", "vt_grand_long", "cs_star_long"
            → long horizon  (T = C.TimeRange, e.g. 150)
    """
    beta = C.Beta_P
    eta  = C.eta
    phi  = C.phi
    psi  = C.Psi
    Z0   = C.Z0
    N    = C.N
    tol  = C.TIE_TOL

    # Short horizon (T = TP, e.g. 60)
    eq_short = _compute_equilibrium(N, C.TP, beta, eta, phi, psi, Z0, tol)
    res = _build_result(eq_short, N, C.TP, beta, eta, phi, psi, Z0)

    # Long horizon (T = TimeRange, e.g. 150)
    eq_long = _compute_equilibrium(N, C.TimeRange, beta, eta, phi, psi, Z0, tol)
    res_long = _build_result(eq_long, N, C.TimeRange, beta, eta, phi, psi, Z0)

    # Merge long-horizon results under suffixed keys
    res["vt_small_long"] = res_long["vt_small"]
    res["vt_big_long"]   = res_long["vt_big"]
    res["vt_grand_long"] = res_long["vt_grand"]
    res["cs_star_long"]  = res_long["cs_star"]

    return res
