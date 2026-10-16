from pathlib import Path

import pytest

from tewii.core import check_deps


def test_no_deps(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PATH", str(tmp_path))

    with pytest.raises(
        RuntimeError,
        match="Required dependencies 'pandoc' and/or 'pdflatex' are not installed",
    ):
        check_deps()
