# constants.py — lean, paper-first naming

# Preferences
Beta_P = 0.99   # β^P (politicians)
Beta_E = 0.99   # β^E (experts)

# Horizons
TP = 60  # optional finite horizon for evaluation (e.g. 30, 100)
TimeRange = 60 # fallback "infinite" horizon

# Environment
eta = 0.3      # η in π_i,t = 0.5*q_i,t^2 + η·Z_t
phi = 0.99    # ϕ in Z_{t+1} = ϕ·Z_t + Ψ − (q_t·members)
Psi = 10000       # Ψ exogenous inflow 

# Beliefs
phi_expert = 0.99
phi_true = None
phi_politician = None

# Geometry / initial state
N = 25          # number of countries explored
Z0 = 1000000        # initial stock

# Numerics
ROUNDING_MODE = "none"
TIE_TOL = 1e-8
