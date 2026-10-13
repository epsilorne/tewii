import getpass
import os
import subprocess
from datetime import date
from json import JSONDecodeError
from pathlib import Path
from textwrap import dedent

from watchdog.observers import Observer

from tewii.project import Project
from tewii.workers import SourceFileMonitor


def initial_files(project_name: str) -> dict[str, str]:
    """Return a dictionary of starting files to include in a project.

    Each key is the file name, and each value is the file's contents. Note this
    only supports *files*; directories are not supported.

    Args:
        project_name (str): The name of the project, which fills the doc's title
    """
    return {
        "document.md": dedent(f"""\
        ---
        title: "{project_name}"
        author: "{getpass.getuser()}"
        date: "{date.today()}"
        titlepage: true
        documentclass: report
        ---

        # Starting Document
        This is an example document written in Markdown, which will also be rendered into LaTeX!
        """)
    }


def init_project(project_name: str) -> str:
    """Initialise a new project, specified by the given name (which can also be
    a path to somewhere).

    This will create a directory for the project based on its name, a .tewii.json
    to store project metadata, and any initial files required for the project.

    Args:
        project_name (str): The name of the project

    Returns:
        str: A message, determining success or failure (i.e. when a project or
        directory with the same name already exists)

    """
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

        # Then, create all the starter files for the project
        for name, contents in initial_files(project_name).items():
            with open(project_path / name, "w") as file:
                file.write(contents)

        return f"Initialised an empty Tewii project in {project_path.resolve()}"


def edit_project(project_name: str) -> str:
    """Begin editing a project by opening its source file into the user's editor.

    This function checks if the project exists (based on a .tewii.json file) and
    if it does, reads the project metadata into memory and opens the first source
    file into the user's preferred text editor.

    Args:
        project_name (str): The name of the project

    Returns:
        str: A message, determining success or failure (i.e. when a project does
        not exist, or its .tewii.json is broken)

    """
    project_path = Path(project_name)
    tewii_project_file = project_path / ".tewii.json"

    if tewii_project_file.exists():
        current_project = None

        with open(tewii_project_file, "r") as file:
            try:
                current_project = Project.from_json(file.read())
            except TypeError:
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

            # Use a 'watchdog' to begin monitoring project source files for any
            # changes (which'll trigger Pandoc + Pdflatex to render)
            file_monitor = SourceFileMonitor(current_project, project_path.resolve())
            observer = Observer()
            observer.schedule(
                file_monitor, str(project_path.resolve()), recursive=False
            )
            observer.start()

            try:
                # TODO: needs to be OS-agnostic (e.g. for windows)
                subprocess.run(
                    [os.environ["EDITOR"], source_file],
                    check=True,
                    cwd=project_path,
                )

            finally:
                observer.stop()
                observer.join()

            # TODO: git handling here
            return "Ok"
    else:
        return f"A Tewii project does not exist at {project_path.resolve()}"
