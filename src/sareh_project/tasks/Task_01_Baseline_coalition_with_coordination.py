# Coalition Formation With Coordination
import json
import numpy as np
import pandas as pd
from sareh_project.tasks._io import table_path
import sareh_project.model.constants as C
from sareh_project.model.coalition_with_coordination import compute_coalition_with_coordination
from sareh_project.model.notation import format_structure


def task_01_coalition_with_coordination():
    """
    Solve WITH coordination (overarching agreements allowed) at both
    horizons (T = TP, short/myopic; T = TimeRange, long) and export:
      bld/tables/01_with_coord.txt          (TSV, short horizon, for quick inspection)
      bld/tables/with_coordination.json     (full snapshot: both horizons,
                                              including the Z_t path for each N,
                                              as named in the project README)
    """
    res = compute_coalition_with_coordination()
    Nmax = C.N

    df = pd.DataFrame(
        dict(
            N=np.arange(1, Nmax + 1, dtype=int),
            cs_star=[format_structure(cs) for cs in res["cs_star"]],
            vt_small=np.asarray(res["vt_small"], float),
            vt_big=np.asarray(res["vt_big"], float),
            vt_grand=np.asarray(res["vt_grand"], float),
            cs_star_long=[format_structure(cs) for cs in res["cs_star_long"]],
            vt_small_long=np.asarray(res["vt_small_long"], float),
            vt_big_long=np.asarray(res["vt_big_long"], float),
            vt_grand_long=np.asarray(res["vt_grand_long"], float),
        )
    )
    out = table_path("01_with_coord")
    df.to_csv(out, index=False, sep="\t")

    snapshot = {
        "N": Nmax,
        "TP": C.TP,
        "TimeRange": C.TimeRange,
        "cs_star": [format_structure(cs) for cs in res["cs_star"]],
        "vt_small": list(map(float, res["vt_small"])),
        "vt_big": list(map(float, res["vt_big"])),
        "vt_grand": list(map(float, res["vt_grand"])),
        "z_paths": [z.tolist() for z in res["z_paths"]],
        "cs_star_long": [format_structure(cs) for cs in res["cs_star_long"]],
        "vt_small_long": list(map(float, res["vt_small_long"])),
        "vt_big_long": list(map(float, res["vt_big_long"])),
        "vt_grand_long": list(map(float, res["vt_grand_long"])),
        "z_paths_long": [z.tolist() for z in res["z_paths_long"]],
    }
    json_out = table_path("with_coordination").with_suffix(".json")
    with open(json_out, "w") as f:
        json.dump(snapshot, f)

    return {"table": str(out), "json": str(json_out)}
