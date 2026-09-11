# src/sareh_project/tasks/inter_index_core.py
from __future__ import annotations
import numpy as np

import sareh_project.model.constants as C
from sareh_project.model.coalition_with_coordination import (
    compute_coalition_with_coordination,
)
from sareh_project.model.coalition_without_coordination import (
    compute_coalition_without_coordination,
)

def _ii_from_parts(N: int, parts: list[int]) -> float:
    # II = (sum of m^2 across coalitions) / N^2
    # because total abatement per coalition of size m is m * q_i(m)
    # and q_i(m) ∝ m, so totals ∝ m^2; constants cancel in the ratio.
    num = float(sum(int(m) * int(m) for m in parts))
    den = float(N * N)
    return num / den if den else 0.0

def compute_inter_index(
    with_coord: bool,
    *,
    betaP: float | None = None,
    TP: int | None = None,
):
    """Return (Ns, II) built from the *equilibrium* coalition structures.

    - Uses the appropriate coalition solver to get cs_star for each N.
    - Computes II(N) = Σ m^2 / N^2 (paper definition via abatement totals).
    """
    old_beta, old_tp = C.Beta_P, getattr(C, "TP", None)
    if betaP is not None:
        C.Beta_P = float(betaP)
    if TP is not None:
        C.TP = int(TP)

    try:
        solver = (
            compute_coalition_with_coordination
            if with_coord
            else compute_coalition_without_coordination
        )
        res = solver()
        cs_star = res["cs_star"]

        Ns = np.arange(2, C.N + 1, dtype=int)
        II = np.empty_like(Ns, dtype=float)

        for i, N in enumerate(Ns):
            parts = cs_star[N - 1] or [N]
            II[i] = _ii_from_parts(N, parts)

        return Ns, II
    finally:
        C.Beta_P = old_beta
        C.TP = old_tp
