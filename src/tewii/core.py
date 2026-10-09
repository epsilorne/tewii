from pathlib import Path

from tewii.project import Project


def init_project(project_name: str) -> str:
    project_path = Path(project_name)
    project_path.mkdir(parents=True, exist_ok=True)

    tewii_project_file = project_path / ".tewii.json"

    if tewii_project_file.exists():
        return f"A Tewi project already exists in {project_path.resolve()}"
    else:
        # For an empty project we need to create a template project file
        # for the editing command (and later the git repo)
        with open(tewii_project_file, "w") as file:
            file.write(Project(project_path.name).to_json())

        return f"Initialised an empty Tewi project in {project_path.resolve()}"
