from pathlib import Path

# Base dirs
BLD = Path("bld")
FIG = BLD / "figures"
TAB = BLD / "tables"
TXT = BLD / "text"

for d in (FIG, TAB, TXT):
    d.mkdir(parents=True, exist_ok=True)

def fig_path(name: str) -> Path:
    if not name.endswith(".png"): name += ".png"
    return FIG / name

def table_path(name: str) -> Path:
    # Project-wide convention: tables & text artifacts use .txt
    if not name.endswith(".txt"):
        name += ".txt"
    return TAB / name

def text_path(name: str) -> Path:
    if not name.endswith(".txt"): name += ".txt"
    return TXT / name
