# emission_abatement.py

import numpy as np
from . import constants as C

def emission_abatement(M: np.ndarray) -> np.ndarray:
    # q*(m) = m * β_E * η / (1 − β_E * ϕ)
    m = M[:, 0].astype(float)
    return m * C.Beta_E * C.eta / (1.0 - C.Beta_E * C.phi)
