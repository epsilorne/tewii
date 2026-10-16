"""Test project editing functionality.

Since editing is blocking under normal circumstances until the editor is closed,
we can only test for the negative cases.
"""

from pathlib import Path
from textwrap import dedent

import pytest

from tewii.core import edit_project, init_project

DUMMY_PROJECT_NAME = "example"
INVALID_PROJECT_FILE = dedent("""\
{
    "improper_field": "report"
}
""")
MALFORMED_PROJECT_FILE = dedent("""\
{
    bad_json
""")


def test_edit_project_does_not_exist(tmp_path: Path):
    project_path = tmp_path / DUMMY_PROJECT_NAME
    result = edit_project(str(project_path))

    assert result == f"A Tewii project does not exist at {project_path}"


def test_edit_project_bad_json(tmp_path: Path):
    project_path = tmp_path / DUMMY_PROJECT_NAME
    init_project(str(project_path))

    with open(project_path / ".tewii.json", "w") as file:
        file.write(INVALID_PROJECT_FILE)

    with pytest.raises(
        RuntimeError,
        match=f"{project_path / '.tewii.json'} is an invalid Tewii project file",
    ):
        edit_project(str(project_path))


def test_edit_project_malformed_json(tmp_path: Path):
    project_path = tmp_path / DUMMY_PROJECT_NAME
    init_project(str(project_path))
    with open(project_path / ".tewii.json", "w") as file:
        file.write(MALFORMED_PROJECT_FILE)

    with pytest.raises(
        RuntimeError,
        match=f"{project_path / '.tewii.json'} contains malformed JSON",
    ):
        edit_project(str(project_path))


def test_edit_project_no_source_files(tmp_path: Path):
    project_path = tmp_path / DUMMY_PROJECT_NAME
    init_project(str(project_path))
    (project_path / "document.md").unlink()

    with pytest.raises(
        RuntimeError,
        match=f"Could not find any existing source files to edit. Check {project_path / '.tewii.json'} and try again",
    ):
        edit_project(str(project_path))
