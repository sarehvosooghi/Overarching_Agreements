# Assembles a Table B.1-style table for Sections 3-4 of the paper: pure
# Ray-Vohra equilibrium coalition structure M* (no overarching agreements
# anywhere), comparing WITH separation of power (technocrats set q*(m),
# eq. 4.1) against WITHOUT separation of power (myopic politicians set
# their own q_hat(m,T), eq. 2.5), at a low horizon T_LOW and a longer
# horizon T_HIGH.
import numpy as np
import pandas as pd
from sareh_project.tasks._io import table_path
import sareh_project.model.constants as C
from sareh_project.model.coalition_without_coordination import solve as solve_with_sop
from sareh_project.model.coalition_without_coordination_myopic import solve as solve_without_sop
from sareh_project.model.notation import format_structure

T_LOW = 40     # short/myopic horizon shown in the left-hand pair of columns
T_HIGH = 150   # long horizon shown in the right-hand pair of columns


def _tex_cell(value) -> str:
    s = str(value)
    if "^" in s:
        return f"${s}$"
    return s.replace("_", r"\_")


def _to_latex_booktabs(df: pd.DataFrame) -> str:
    cols = [_tex_cell(c) for c in df.columns]
    lines = [r"\begin{tabular}{" + "l" * len(cols) + "}", r"\toprule",
             " & ".join(cols) + r" \\", r"\midrule"]
    for _, row in df.iterrows():
        lines.append(" & ".join(_tex_cell(v) for v in row) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(lines) + "\n"


def task_05_table_separation_of_power():
    """
    Outputs:
      bld/tables/table_separation_of_power.txt   (TSV)
      bld/tables/table_separation_of_power.tex   (LaTeX, booktabs-style)
    """
    Nmax = C.N

    sop_low   = solve_with_sop(N_max=Nmax, horizon=T_LOW)
    sop_high  = solve_with_sop(N_max=Nmax, horizon=T_HIGH)
    nosop_low  = solve_without_sop(N_max=Nmax, horizon=T_LOW)
    nosop_high = solve_without_sop(N_max=Nmax, horizon=T_HIGH)

    df = pd.DataFrame(
        {
            "N": np.arange(1, Nmax + 1, dtype=int),
            f"separation of power (T={T_LOW})": [format_structure(cs) for cs in sop_low["cs_star"]],
            f"w/o separation of power (T={T_LOW})": [format_structure(cs) for cs in nosop_low["cs_star"]],
            f"separation of power (T={T_HIGH})": [format_structure(cs) for cs in sop_high["cs_star"]],
            f"w/o separation of power (T={T_HIGH})": [format_structure(cs) for cs in nosop_high["cs_star"]],
        }
    )

    out_txt = table_path("table_separation_of_power")
    df.to_csv(out_txt, index=False, sep="\t")

    out_tex = out_txt.with_suffix(".tex")
    with open(out_tex, "w") as f:
        f.write(_to_latex_booktabs(df))

    return {"table_txt": str(out_txt), "table_tex": str(out_tex)}
