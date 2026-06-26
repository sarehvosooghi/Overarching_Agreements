# Coalition Formation Without Coordination
import numpy as np
import pandas as pd
from sareh_project.tasks._io import table_path
import sareh_project.model.constants as C
from sareh_project.model.coalition_without_coordination import compute_coalition_without_coordination
def task_02_coalition_without_coordination():
    """
    Solve WITHOUT coordination and export vt_small, vt_big, vt_grand, cs_star.
    Outputs:
      bld/tables/02_without_coord.txt (TSV)
    """
    res = compute_coalition_without_coordination()
    Nmax = C.N
    df = pd.DataFrame(
        dict(
            N=np.arange(1, Nmax + 1, dtype=int),
            vt_small=np.asarray(res["vt_small"], float),
            vt_big=np.asarray(res["vt_big"], float),
            vt_grand=np.asarray(res["vt_grand"], float),
            cs_star=[str(cs) for cs in res["cs_star"]],
        )
    )
    out = table_path("02_without_coord")
    df.to_csv(out, index=False, sep="\t")
    return {"table": str(out)}
