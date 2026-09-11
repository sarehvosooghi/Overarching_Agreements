# simulation_myopic.py
#
# Copy of simulation.py's run_simulation(), with the ONE change needed to
# get the "without separation of power" case of Sections 3-4: it calls
# emission_abatement_myopic(M, T) -- equation (2.5), the MYOPIC POLITICIAN's
# own abatement choice -- instead of emission_abatement(M) -- equation
# (4.1), the non-myopic TECHNOCRAT's choice used everywhere else in this
# project under separation of power. See README.txt, section "SEPARATION OF
# POWER (SECTIONS 3-4) TABLE" for what to edit if you want a single switchable
# run_simulation instead of two parallel copies.

import numpy as np
from . import constants as C
from .emission_abatement_myopic import emission_abatement_myopic
from .global_emissions import global_emissions

def run_simulation_myopic(
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
        q = emission_abatement_myopic(M, T)   # per size-class, per-member abatement -- eq. (2.5)
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


def simulate_Z_path_myopic(
    M: np.ndarray,
    *,
    horizon: int,
    T_path: int = 200,
    phi_choice: float | None = None,
    phi_state: float | None = None,
    Z0: float | None = None,
) -> np.ndarray:
    """Z_t path (t=0,...,T_path) under the myopic politician's abatement
    q_hat(m, horizon) -- unlike simulate_Z_path() for the technocrat case,
    this one DOES need the horizon, since q_hat depends on it."""
    phi_choice = float(phi_choice if phi_choice is not None else C.phi_expert)
    phi_state  = float(phi_state  if phi_state  is not None else (C.phi_true if C.phi_true is not None else phi_choice))
    Z = float(Z0 if Z0 is not None else C.Z0)

    old_phi = C.phi
    try:
        C.phi = phi_choice
        q = emission_abatement_myopic(M, horizon)
        C.phi = phi_state

        Z_path = np.empty(T_path + 1, dtype=float)
        Z_path[0] = Z
        for t in range(1, T_path + 1):
            Z = global_emissions(Z, q, M)
            Z_path[t] = Z

        return Z_path
    finally:
        C.phi = old_phi
