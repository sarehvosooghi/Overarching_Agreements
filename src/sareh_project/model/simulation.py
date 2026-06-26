# simulation.py

import numpy as np
from . import constants as C
from .emission_abatement import emission_abatement
from .global_emissions import global_emissions

def run_simulation(
    M: np.ndarray,
    *,
    horizon: int | None = None,
    beta: float | None = None,
    phi_choice: float | None = None,
    phi_state: float | None = None,
    Z0: float | None = None,
) -> np.ndarray:
    T = int(horizon if horizon is not None else (C.TP if C.TP is not None else C.TimeRange))
    beta_p = float(beta if beta is not None else C.Beta_P)
    phi_choice = float(phi_choice if phi_choice is not None else C.phi_expert)
    phi_state  = float(phi_state  if phi_state  is not None else (C.phi_true if C.phi_true is not None else phi_choice))
    Z = float(Z0 if Z0 is not None else C.Z0)

    old_phi = C.phi
    try:
        C.phi = phi_choice
        q = emission_abatement(M)     # per size-class, per-member abatement
        C.phi = phi_state

        K = M.shape[0]
        V = np.zeros((T, K), dtype=float)
        cum = np.zeros(K, dtype=float)

        for t in range(T):
            loss_t = 0.5 * (q**2) + C.eta * Z      # vector over classes
            cum += (beta_p ** t) * loss_t
            V[t] = cum
            Z = global_emissions(Z, q, M)

        return V
    finally:
        C.phi = old_phi
