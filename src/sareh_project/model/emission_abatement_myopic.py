# emission_abatement_myopic.py
#
# Implements q_hat_i(m,T), equation (2.5) of the paper: the abatement chosen
# by a MYOPIC POLITICIAN with a rolling T-period horizon herself (Section 3),
# as opposed to q*(m), equation (4.1), which is the abatement chosen by a
# non-myopic TECHNOCRAT under separation of power (Section 4, implemented in
# emission_abatement.py).
#
#   q_hat_i(m, T) = C'^{-1}( m * beta_P * B3(T-1) )
#   B3(T)         = eta * (1 - (phi * beta_P)**T) / (1 - phi * beta_P)
#
# With the quadratic cost function C(q) = q**2 / 2 used throughout this
# project, C'(q) = q so C'^{-1}(x) = x, giving:
#
#   q_hat(m, T) = m * beta_P * eta * (1 - (phi * beta_P)**(T-1)) / (1 - phi * beta_P)
#
# Unlike q*(m), q_hat(m, T) depends explicitly on the horizon T (it is
# strictly increasing in T, per Lemma 1, and converges to q*(m) only in the
# limit T -> infinity, per Corollary 1). It is still stationary in time t
# for a FIXED T (Lemma 1), so -- exactly like emission_abatement.py -- it
# only needs to be evaluated once per (M, T) pair.

import numpy as np
from . import constants as C

def emission_abatement_myopic(M: np.ndarray, T: int) -> np.ndarray:
    m = M[:, 0].astype(float)
    beta_p = C.Beta_P
    B3_Tminus1 = C.eta * (1.0 - (C.phi * beta_p) ** (T - 1)) / (1.0 - C.phi * beta_p)
    return m * beta_p * B3_Tminus1
