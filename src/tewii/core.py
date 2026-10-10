from json import JSONDecodeError
import os
from pathlib import Path
import subprocess

from tewii.project import Project


def init_project(project_name: str) -> str:
    project_path = Path(project_name)
    project_path.mkdir(parents=True, exist_ok=True)

    tewii_project_file = project_path / ".tewii.json"

    if tewii_project_file.exists():
        return f"A Tewii project already exists in {project_path.resolve()}"
    else:
        # For an empty project we need to create a template project file
        # for the editing command (and later the git repo)
        with open(tewii_project_file, "w") as file:
            file.write(Project(project_path.name).to_json())

        (project_path / "document.md").touch()

        return f"Initialised an empty Tewii project in {project_path.resolve()}"


def edit_project(project_name: str) -> str:
    project_path = Path(project_name)
    tewii_project_file = project_path / ".tewii.json"

    if tewii_project_file.exists():
        current_project = None

        with open(tewii_project_file, "r") as file:
            try:
                current_project = Project.from_json(file.read())
            except TypeError as e:
                raise RuntimeError(
                    f"{tewii_project_file.resolve()} is an invalid Tewii project file"
                )
            except JSONDecodeError:
                raise RuntimeError(
                    f"{tewii_project_file.resolve()} contains malformed JSON"
                )

            # Find the first existing file in current_project.source_files
            source_file = next(
                (
                    file
                    for file in current_project.source_files
                    if (project_path / file).exists()
                ),
                None,
            )
            if source_file is None:
                return f"Could not find any existing source files to edit. Check {tewii_project_file.resolve()} and try again"

            # TODO: needs to be OS-agnostic (e.g. for windows)
            subprocess.run(
                [os.environ["EDITOR"], source_file],
                check=True,
                cwd=project_path,
            )

            # TODO: git handling here
            return "Ok"
    else:
        return f"A Tewii project does not exist at {project_path.resolve()}"
