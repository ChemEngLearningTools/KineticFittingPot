from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "modules" / "batch_reactors.py"
DOC = ROOT / "docs" / "BATCH_REACTOR_FUNDAMENTALS.md"
HOME = ROOT / "modules" / "home.py"
HELP = ROOT / "modules" / "help_about.py"


def main() -> None:
    page = PAGE.read_text(encoding="utf-8")
    doc = DOC.read_text(encoding="utf-8")
    home = HOME.read_text(encoding="utf-8")
    help_text = HELP.read_text(encoding="utf-8")

    required_page = [
        "From industrial multipurpose batch operation",
        "What is a batch reactor?",
        "multipurpose vessels",
        "operations list",
        "Pure batch and semi-batch operation",
        "pure batch reaction",
        "semi-batch operation",
        "What does a real batch reactor look like?",
        "glass-lined internal surface",
        "external jacket",
        "From industrial operation to the first KineticFittingPot model",
        "Industrial batch process",
        "First KineticFittingPot model",
        "Later KineticFittingPot models",
        "Why start with the simplified model?",
        "pure-batch reaction period",
        "the later fed-batch model restores the inlet term explicitly",
        r"\frac{d(\rho V)}{dt}=0",
        r"\boxed{\frac{dn_j}{dt}=V R_j}",
        r"\boxed{\frac{d\mathbf{n}}{dt}=V\,\mathbf{S}\,\mathbf{r}}",
    ]
    for marker in required_page:
        assert marker in page, marker

    forbidden = [
        "overwhelmingly the most common",
        "by orders of magnitude",
        "millions of pounds per tonne",
        "blue coloured glass",
        "1-3mm thick",
    ]
    for marker in forbidden:
        assert marker not in page, marker

    for marker in [
        "operations list",
        "pure batch",
        "semi-batch",
        "Industrial-to-model progression",
        "Later KineticFittingPot models",
    ]:
        assert marker in doc, marker

    assert "industrial multipurpose batch vessel" in home
    assert "operations-list concept" in help_text

    print("PASS: Batch Reactor Fundamentals v1.49 industrial-context revision")


if __name__ == "__main__":
    main()
