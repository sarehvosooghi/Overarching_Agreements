## COALITION FORMATION — PYTHON (PIXI + PYTASK)

This project reproduces coalition-formation results from paper 'Overarching Agreements and Separation of Power from Myopic Politicians'by Sareh Vosooghi, in Python.
It computes equilibrium coalition structures (with and without possibility of proposing overarching agreements/coordination),
and assembles the results tables as TSV, JSON, LaTeX, and PNG (Z_t path figures).

Key points

* All parameters live in one Python file (no .txt loaders).
* All tasks are carried out with one PyTask command and run via Pixi.
* Outputs (tables and figures) are written under bld/tables/ and bld/figures/.

---

1. QUICK START

---

Open a terminal at the project root.

Run all tasks:
pixi run pytask

Force re-run even if PyTask thinks nothing changed:
pixi run pytask --force

---

2. WHAT GETS CREATED (bld/)

---

bld/
tables/
with_coordination.json              # full equilibrium snapshot (with coordination/overarching agreement), both horizons, incl. Z_t path per N
without_coordination.json           # full equilibrium snapshot (without coordination/overarching agreement), both horizons, incl. Z_t path per N
01_with_coord.txt                   # TSV summary (with coordination), both horizons
02_without_coord.txt                # TSV summary (without coordination), both horizons
table_B1.txt / table_B1.tex         # assembled Table B.1 of the paper: M* with/without overarching, at T=TP and T=TimeRange, side by side
figures/
Z_path_with_coordination_T{TP}.png
Z_path_without_coordination_T{TP}.png
Z_path_with_coordination_T{TimeRange}.png
Z_path_without_coordination_T{TimeRange}.png

---

3. DIRECTORY LAYOUT (src/)

---

src/
	sareh_project/
		**init**.py
		model/
			**init**.py
			constants.py                 # all model parameters (edit here)  
			decomposition.py             # integer partitions of N            
			emission_abatement.py        # q(M) per size-class   --- this is under separation of power and quadratic cost function. For the case without technocrats, only this file needs to be eited.            
			global_emissions.py          # S_{t+1}(S_t, q, M)                
			simulation.py                # discounted losses, horizons, phi; also simulate_Z_path (Z_t out to T_path periods, e.g. 200)
			notation.py                  # formats a coalition structure with the paper's superscript notation, e.g. [1,1,1,1] -> "1^4"
			coalition_with_coordination.py   
			coalition_without_coordination.py           
		tasks/
			**init**.py
			Task_01_Baseline_coalition_with_coordination.py     #term coordination is equivalent to overarching agreement
			Task_02_Baseline_coalition_without_coordination.py  #term coordination is equivalent to overarching agreement
			Task_03_table_B1.py                                 # assembles Table B.1 (both scenarios x both horizons)
			Task_04_Z_path_figures.py                           # plots Z_t path, both scenarios x both horizons

---

4. TABLES 

---

Table B.2 of the paper is reproduced by Task_03 (bld/tables/table_B1.txt / .tex): for each N = 1,...,C.N it
reports M* with and without the possibility of proposing overarching agreements, at T = TP (short/myopic
column) and T = TimeRange (long column, approximating the infinite horizon). Coalition structures are
printed with the paper's superscript notation, e.g. "1^4" rather than "1,1,1,1".

---

5. PARAMETERS — WHERE TO EDIT

---

Edit parameters in:
src/sareh_project/model/constants.py  


Important runtime behavior
Model modules read constants at runtime (imported as C), so tasks can set
constants like TP or eta/beta just before a run and restore afterward.
(This is how TP comparisons and eta_P applications are implemented.)

---

6. WHAT EACH TASK DOES (SHORT REFERENCE)

---

Core equilibrium snapshots
Task_01_Baseline_coalition_with_coordination.py    -> bld/tables/with_coordination.json, 01_with_coord.txt  --> with possibility of overarching agreements
Task_02_Baseline_coalition_without_coordination.py -> bld/tables/without_coordination.json, 02_without_coord.txt --> without possibility of overarching agreements
Task_03_table_B1.py                                -> bld/tables/table_B1.txt, table_B1.tex --> assembled Table B.1 of the paper
Task_04_Z_path_figures.py                          -> bld/figures/Z_path_*.png --> Z_t path (t=0,...,200) for a handful of representative N, both scenarios, both horizons

---

7. MODEL OVERVIEW (MECHANICS)

---

Partitions (decomposition.py)
Enumerates all integer partitions of N (1..N blocks) used as candidates.  

Abatement rule (emission_abatement.py) This is under the assumption of separation of power, and quadratic cost function assumption. 
Per-member abatement for a size class m:
q(m) = m * beta2 * gamma / (1 - beta2 * phi)                         

Stock update (global_emissions.py)
S_{t+1} = phi * S_t + natural_emissions - q_t @ M[:, 1]
where q_t contains one per-member abatement per size class, and M[:, 1]
is the number of members in that class (size × count).                    

Discounted loss accumulation (simulation.py)
Per member in a size class at period t:
cost_t = q_t**2 / 2
loss_t = cost_t + gamma * S_t
Cumulated up to horizon T with politicians’ beta:
V_T = sum_{t=0..T-1} (beta^t) * loss_t
Horizon handling: if TP is None, the long horizon TimeRange is used.

Z_t path (simulation.py: simulate_Z_path)
Since q(m) is stationary, the abatement schedule implied by an equilibrium
structure M can be rolled forward for as many periods as we like (default
200), independently of the horizon T used to rank structures. This is used
to report and plot the path of Z_t under M*, for both scenarios and both
horizons.

Equilibrium selection with and without coordination/overarching agreements (coalition_* files)
coalition_without_coordination.py is the pure Ray and Vohra (2001) backward
recursion: for n = 1,...,N it filters candidate partitions by a stability
check (a partition's prefix, i.e. all but the last block, must match the
already-computed equilibrium of the residual subgame n - last_block), then
selects the partition that minimises the smallest-coalition-member loss
(ties resolved deterministically, preferring the larger smallest block).
Overarching agreements are NEVER injected here. 

coalition_with_coordination.py runs its own backward recursion, in which
overarching agreements are checked at EVERY n (not only at n=N — the
negotiating room can shrink to any size n<N during the sequential
bargaining process, and an overarching agreement can be proposed among
whichever n countries are active at that point). At each n, three kinds of
candidates are compared: (a) the grand coalition {n}; (b) for every m with
1<=m<=n-1 AND m no larger than the smallest block already present in
equil[n-m]: a single, freshly-proposed, independent coalition of size m,
peeled off, combined with the already-recursively-computed continuation
equil[n-m] (which may itself already contain an overarching sub-block from
an earlier step — e.g. equil[10] can be {5,5}, so that n=11 can pick up
{5,5,1}); and (c) for every proper divisor k of n such that the
sub-coalition of size n/k is not itself an independent equilibrium
(equil[n/k] != (n/k,), i.e. Section 5.2's "comparatively fragmented"
condition): the overarching agreement {(n/k)^k}. Whichever candidate has
the lowest smallest-coalition-member loss is chosen.




---

8. NOTES AND TROUBLESHOOTING

---

These Python codes were written and tested on a MacBook; Windows users may need to make minor adjustments, especially to file paths and environment settings.


Python exponent vs XOR
In Python, 10^5 equals 15 (XOR). If you intend one hundred thousand, use:
S0 = 100000   or   S0 = 10**5   or   S0 = 1e5




Make sure **init**.py files exist in src/sareh_project/ and its subfolders.



---

9. SEPARATION OF POWER (SECTIONS 3-4) TABLE

---

Table B1 in the paper comparing WITH vs
WITHOUT separation of power (instead of with vs without overarching
agreements) is produced by a self-contained set of files. No
overarching agreements are ever considered here -- this reproduces
Sections 3 and 4 of the paper, which precede the introduction of
overarching agreements in Section 5.

New files:
  model/emission_abatement_myopic.py         -> q_hat_i(m,T), eq. (2.5): the
                                                 MYOPIC POLITICIAN's own
                                                 abatement choice (Section 3),
                                                 as opposed to q*(m), eq.
                                                 (4.1), in emission_abatement.py,
                                                 which is the TECHNOCRAT's
                                                 choice under separation of
                                                 power (Section 4). Unlike
                                                 q*(m), q_hat(m,T) depends on
                                                 the horizon T explicitly.
  model/simulation_myopic.py                 -> run_simulation_myopic() /
                                                 simulate_Z_path_myopic(): exact
                                                 copies of simulation.py's
                                                 functions, with q computed via
                                                 emission_abatement_myopic(M,T)
                                                 instead of emission_abatement(M).
  model/coalition_without_coordination_myopic.py
                                              -> the "without separation of
                                                 power" equilibrium: the SAME
                                                 pure Ray & Vohra (2001)
                                                 recursion as
                                                 coalition_without_coordination.py
                                                 (no overarching agreements),
                                                 just built on
                                                 run_simulation_myopic()
                                                 instead of run_simulation().
  tasks/Task_05_table_separation_of_power.py -> bld/tables/table_separation_of_power.txt / .tex
                                                 Compares "separation of power"
                                                 (coalition_without_coordination.solve,
                                                 i.e. q*(m)) against "w/o
                                                 separation of power"
                                                 (coalition_without_coordination_myopic.solve,
                                                 i.e. q_hat(m,T)), at T_LOW=40
                                                 and T_HIGH=150 (set at the top
                                                 of the task file, independent
                                                 of C.TP/C.TimeRange).





  1. In emission_abatement.py, emission_abatement(M) implements q*(m),
     eq. (4.1) -- the technocrat rule, independent of T. To get the
     politician's own eq. (2.5) rule instead, this is the ONE function
     that must change: it needs to also take the horizon T as an argument
     and return q_hat(m,T) = m * Beta_P * B3(T-1), with
     B3(T) = eta * (1 - (phi*Beta_P)**T) / (1 - phi*Beta_P)
     (see emission_abatement_myopic.py for the literal formula).
  2. In simulation.py, run_simulation() calls
     q = emission_abatement(M)
     This is the ONE call site that would need to change to
     q = emission_abatement(M, T)  (or a myopic/technocrat flag) if
     emission_abatement() is extended per (1) to take T.
  3. Nothing in decomposition.py, global_emissions.py,
     coalition_without_coordination.py, or coalition_with_coordination.py
     needs to change -- they only ever call run_simulation()/
     simulate_Z_path() and never touch the abatement rule directly, so
     whichever rule run_simulation() ends up using (q*(m) or q_hat(m,T))
     flows through automatically to every coalition-formation computation
     and to Table B.1 and this table alike.



---

## APPENDIX: FILE ANCHORS

Key implementation points are visible in:
coalition_with_coordination.py  (pure continuation reuse, overarching candidates checked only at n=N, selection)
coalition_without_coordination.py (stability, selection baseline, Z_t path, two-horizon wrapper)
notation.py (superscript formatting for Table B.1, e.g. "1^4")
constants.py (parameters, horizons, phi knobs, rounding, S0)                    
decomposition.py (partitions)                                                   
emission_abatement.py (q* rule, eq. 4.1, technocrat/separation-of-power)
emission_abatement_myopic.py (q_hat rule, eq. 2.5, myopic-politician/no-separation-of-power)
global_emissions.py (stock recursion, q_t @ M[:,1])                              
simulation.py (loss accumulation, horizons, phi choice/state separation, Z_t path)
simulation_myopic.py (same as simulation.py, but built on emission_abatement_myopic)
coalition_without_coordination_myopic.py (Sections 3-4 "without separation of power" baseline)
