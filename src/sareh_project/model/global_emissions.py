# global_emissions.py 

import numpy as np
from . import constants as C

def global_emissions(Z_t: float, q_t: np.ndarray, M: np.ndarray) -> float:
    # Z_{t+1} = ϕ·Z_t + Ψ − (q_t · members)
    return C.phi * Z_t + C.Psi - float(q_t @ M[:, 1])
