## COALITION FORMATION — PYTHON (PIXI + PYTASK)

This project reproduces coalition-formation results from paper 'Overarching Agreements and Separation of Power from Myopic Politicians'by Sareh Vosooghi, in Python.
It computes equilibrium coalition structures (with and without possibility of proposing overarching agreements/coordination),
and assembles the results tables as PNG and LaTeX.

Key points

* All parameters live in one Python file (no .txt loaders).
* All tasks are carried out with one PyTask command and run via Pixi.
* Outputs (tables) are written under bld/tables/.

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
with_coordination.json              # equilibrium snapshot (with coordination/overarching agreement)
without_coordination.json           # equilibrium snapshot (without coordination/overarching agreement)


Diagnostics produce additional TSV/JSON summaries alongside these.

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
			simulation.py                # discounted losses, horizons, phi  
			coalition_with_coordination.py   
			coalition_without_coordination.py           
		tasks/
			**init**.py
			task_01_coalition_with_coordination.py  #term coordination is equivalent to overarching agreement
			task_02_coalition_without_coordination.py  #term coordination is equivalent to overarching agreement
			

---

4. TABLES 

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
task_01_coalition_with_coordination.py    -> bld/tables/with_coordination.json   --> with possibility of overarching agreements
task_02_coalition_without_coordination.py -> bld/tables/without_coordination.json --> without possibility of overarching agreements




---

7. MODEL OVERVIEW (MECHANICS)

---

Partitions (decomposition.py)
Enumerates all integer partitions of N (1..N blocks) used as candidates.  

Abatement rule (emission_abatement.py) This is unde the assumption of separation of power, and quadratic cost function assumption. 
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
                                                               

Equilibrium selection and coordination (coalition_* files)
Candidates are filtered by backward recursin: a partition’s prefix (all but
the last block) must match the previously stored equilibrium of the residual
subgame. Under coordination/overarching assumption, we additionally inject all equal-split partitions
(N/k repeated k times) so they are always evaluated. The chosen equilibrium
minimizes the smallest-coalition loss (ties resolved deterministically by
enumeration order).                                                          


---

8. NOTES AND TROUBLESHOOTING

---

These Python codes were written and tested on a MacBook; Windows users may need to make minor adjustments, especially to file paths and environment settings.


Python exponent vs XOR
In Python, 10^5 equals 15 (XOR). If you intend one hundred thousand, use:
S0 = 100000   or   S0 = 10**5   or   S0 = 1e5



“Nothing changed” after parameter edits
Ensure you are running tasks (pytask) and not an already cached output.
Use:  pixi run pytask --force

Import errors
Make sure **init**.py files exist in src/sareh_project/ and its subfolders.

---




## APPENDIX: FILE ANCHORS

Key implementation points are visible in:
coalition_with_coordination.py  (stability, equal-split injection, selection)  
coalition_without_coordination.py (stability, selection baseline)               
constants.py (parameters, horizons, phi knobs, rounding, S0)                    
decomposition.py (partitions)                                                   
emission_abatement.py (q rule)                                                  
global_emissions.py (stock recursion, q_t @ M[:,1])                              
simulation.py (loss accumulation, horizons, phi choice/state separation)         
