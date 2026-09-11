# Assembles Table B.1 of the paper: equilibrium coalition structure M*,
# with and without the possibility of proposing overarching agreements,
# for T = TP (short/myopic) and T = TimeRange (long), side by side.
import numpy as np
import pandas as pd
from sareh_project.tasks._io import table_path
import sareh_project.model.constants as C
from sareh_project.model.coalition_with_coordination import compute_coalition_with_coordination
from sareh_project.model.coalition_without_coordination import compute_coalition_without_coordination
from sareh_project.model.notation import format_structure


def _tex_cell(value) -> str:
    """
    Escape a cell for LaTeX. In particular, the paper's superscript
    notation (e.g. "11^2,1^3") uses a bare '^', which is a special
    character outside math mode and will not compile as-is -- wrap any
    such cell in $...$ so it renders as a real superscript.
    """
    s = str(value)
    if "^" in s:
        return f"${s}$"
    return s.replace("_", r"\_")


def _to_latex_booktabs(df: pd.DataFrame) -> str:
    """
    Minimal booktabs-style LaTeX table writer, written by hand so this does
    not depend on pandas' DataFrame.to_latex() -- in recent pandas versions
    that method routes through Styler, which requires the optional jinja2
    dependency (not in pixi.toml) and raises ImportError without it.
    """
    cols = [_tex_cell(c) for c in df.columns]
    lines = []
    lines.append(r"\begin{tabular}{" + "l" * len(cols) + "}")
    lines.append(r"\toprule")
    lines.append(" & ".join(cols) + r" \\")
    lines.append(r"\midrule")
    for _, row in df.iterrows():
        lines.append(" & ".join(_tex_cell(v) for v in row) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    return "\n".join(lines) + "\n"


def task_03_table_B1():
    """
    Outputs:
      bld/tables/table_B1.txt   (TSV)
      bld/tables/table_B1.tex   (LaTeX, booktabs-style)
    """
    over = compute_coalition_with_coordination()
    pure = compute_coalition_without_coordination()
    Nmax = C.N

    df = pd.DataFrame(
        {
            "N": np.arange(1, Nmax + 1, dtype=int),
            f"overarching (T={C.TP})": [format_structure(cs) for cs in over["cs_star"]],
            f"w/o overarching (T={C.TP})": [format_structure(cs) for cs in pure["cs_star"]],
            f"overarching (T={C.TimeRange})": [format_structure(cs) for cs in over["cs_star_long"]],
            f"w/o overarching (T={C.TimeRange})": [format_structure(cs) for cs in pure["cs_star_long"]],
        }
    )

    out_txt = table_path("table_B1")
    df.to_csv(out_txt, index=False, sep="\t")

    out_tex = out_txt.with_suffix(".tex")
    with open(out_tex, "w") as f:
        f.write(_to_latex_booktabs(df))

    return {"table_txt": str(out_txt), "table_tex": str(out_tex)}
