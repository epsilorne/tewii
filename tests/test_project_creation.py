"""Test project creation/initialisation functionality."""

from pathlib import Path

from tewii.core import init_project, initial_files

DUMMY_PROJECT_NAME = "example"


def test_create_new_project(tmp_path: Path):
    project_path = tmp_path / DUMMY_PROJECT_NAME
    result = init_project(str(project_path))

    assert result == f"Initialised an empty Tewii project in {project_path}"
    assert (project_path / ".tewii.json").exists()

    for name in initial_files(str(project_path)):
        assert (project_path / name).exists()
        assert (project_path / name).stat().st_size > 0


def test_create_new_project_already_exists(tmp_path: Path):
    init_project(str(tmp_path / DUMMY_PROJECT_NAME))
    result = init_project(str(tmp_path / DUMMY_PROJECT_NAME))

    assert (
        result
        == f"A Tewii project already exists in {(tmp_path / DUMMY_PROJECT_NAME).resolve()}"
    )
