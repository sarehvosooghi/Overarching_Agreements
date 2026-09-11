# Plots the path of the global stock of emissions, Z_t, for t = 0,...,200,
# under the equilibrium coalition structure M*, for a handful of
# representative group sizes N, with and without the possibility of
# overarching agreements, at both horizons T = TP and T = TimeRange.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sareh_project.tasks._io import fig_path
import sareh_project.model.constants as C
from sareh_project.model.coalition_with_coordination import compute_coalition_with_coordination
from sareh_project.model.coalition_without_coordination import compute_coalition_without_coordination
from sareh_project.model.notation import format_structure

# representative group sizes N shown in each figure (capped at C.N)
_SHOWCASE_N = sorted({n for n in (6, 12, 20, C.N) if 1 <= n <= C.N})


def _plot(z_paths, cs_star, title, out_name):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for n in _SHOWCASE_N:
        z = z_paths[n - 1]
        ax.plot(range(len(z)), z, label=f"N={n}, M*={format_structure(cs_star[n - 1])}")
    ax.set_xlabel("t")
    ax.set_ylabel(r"$Z_t$")
    ax.set_title(title)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = fig_path(out_name)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def _plot_N25_comparison(over, pure, T, out_name):
    N = C.N
    fig, ax = plt.subplots(figsize=(7, 4.5))
    z_o = over["z_paths" if T == C.TP else "z_paths_long"][N - 1]
    z_p = pure["z_paths" if T == C.TP else "z_paths_long"][N - 1]
    cs_o = over["cs_star" if T == C.TP else "cs_star_long"][N - 1]
    cs_p = pure["cs_star" if T == C.TP else "cs_star_long"][N - 1]
    ax.plot(range(len(z_o)), z_o, label=f"with overarching, M*={format_structure(cs_o)}")
    ax.plot(range(len(z_p)), z_p, label=f"w/o overarching, M*={format_structure(cs_p)}")
    ax.set_xlabel("t")
    ax.set_ylabel(r"$Z_t$")
    ax.set_title(f"Z_t path for N={N} (T={T})")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out = fig_path(out_name)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def task_04_Z_path_figures():
    """
    Outputs (bld/figures/):
      Z_path_with_coordination_T{TP}.png
      Z_path_without_coordination_T{TP}.png
      Z_path_with_coordination_T{TimeRange}.png
      Z_path_without_coordination_T{TimeRange}.png
      Z_path_N{C.N}_comparison_T{TP}.png       (with vs. w/o overarching, N=C.N, T=TP)
      Z_path_N{C.N}_comparison_T{TimeRange}.png (with vs. w/o overarching, N=C.N, T=TimeRange)
    """
    over = compute_coalition_with_coordination()
    pure = compute_coalition_without_coordination()

    outs = {}
    outs["with_short"] = _plot(
        over["z_paths"], over["cs_star"],
        f"Z_t path with overarching agreements (T={C.TP})",
        f"Z_path_with_coordination_T{C.TP}",
    )
    outs["without_short"] = _plot(
        pure["z_paths"], pure["cs_star"],
        f"Z_t path without overarching agreements (T={C.TP})",
        f"Z_path_without_coordination_T{C.TP}",
    )
    outs["with_long"] = _plot(
        over["z_paths_long"], over["cs_star_long"],
        f"Z_t path with overarching agreements (T={C.TimeRange})",
        f"Z_path_with_coordination_T{C.TimeRange}",
    )
    outs["without_long"] = _plot(
        pure["z_paths_long"], pure["cs_star_long"],
        f"Z_t path without overarching agreements (T={C.TimeRange})",
        f"Z_path_without_coordination_T{C.TimeRange}",
    )
    outs["N25_comparison_short"] = _plot_N25_comparison(
        over, pure, C.TP, f"Z_path_N{C.N}_comparison_T{C.TP}"
    )
    outs["N25_comparison_long"] = _plot_N25_comparison(
        over, pure, C.TimeRange, f"Z_path_N{C.N}_comparison_T{C.TimeRange}"
    )
    return {k: str(v) for k, v in outs.items()}
