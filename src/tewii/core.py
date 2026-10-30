import getpass
import os
import subprocess
import sys
from datetime import date
from json import JSONDecodeError
from pathlib import Path
from textwrap import dedent

import psutil
from watchdog.observers import Observer

from tewii.project import Project
from tewii.util import PANDOC, PDFLATEX
from tewii.workers import SourceFileMonitor, open_pdf_previewer


def check_deps() -> bool:
    """Checks if the runtime dependencies are installed.

    Return:
        bool: True if all required dependencies are installed

    Raises:
        RuntimeError: If the required dependencies are not installed
    """
    try:
        subprocess.run([PANDOC, "--version"], stdout=subprocess.DEVNULL, check=True)
        subprocess.run([PDFLATEX, "--version"], stdout=subprocess.DEVNULL, check=True)

        return True
    except OSError, subprocess.CalledProcessError:
        raise RuntimeError(
            "Required dependencies 'pandoc' and/or 'pdflatex' are not installed"
        )


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
    project_path = Path(project_name).resolve()
    project_path.mkdir(parents=True, exist_ok=True)

    tewii_project_file = project_path / ".tewii.json"

    if tewii_project_file.exists():
        return f"A Tewii project already exists in {project_path}"
    else:
        # For an empty project we need to create a template project file
        # for the editing command (and later the git repo)
        with open(tewii_project_file, "w") as file:
            file.write(Project(project_path.name).to_json())

        # Then, create all the starter files for the project
        for name, contents in initial_files(project_name).items():
            with open(project_path / name, "w") as file:
                file.write(contents)

        return f"Initialised an empty Tewii project in {project_path}"


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
    project_path = Path(project_name).resolve()
    tewii_project_file = project_path / ".tewii.json"

    if tewii_project_file.exists():
        current_project = None

        with open(tewii_project_file, "r") as file:
            try:
                current_project = Project.from_json(file.read())
            except TypeError:
                raise RuntimeError(
                    f"{tewii_project_file} is an invalid Tewii project file"
                )
            except JSONDecodeError:
                raise RuntimeError(f"{tewii_project_file} contains malformed JSON")

            # Find the first existing file in current_project.source_files
            source_file = next(
                (
                    (project_path / file)
                    for file in current_project.source_files
                    if (project_path / file).exists()
                ),
                None,
            )
            if source_file is None:
                raise RuntimeError(
                    f"Could not find any existing source files to edit. Check {tewii_project_file} and try again"
                )
            check_deps()

            # Use a 'watchdog' to begin monitoring project source files for any
            # changes (which'll trigger Pandoc + Pdflatex to render)
            file_monitor = SourceFileMonitor(current_project, project_path)
            observer = Observer()
            observer.schedule(file_monitor, str(project_path), recursive=False)
            observer.start()

            # TODO: have another watchdog to monitor the project file, and if it
            # updates, update/recreate the current_project accordingly

            # Also create a background process to handle the pdf preview
            open_pdf_previewer(current_project, project_path)

            # Try EDITOR env var (for Unix), otherwise fallback to OS-defaults
            try:
                if editor := os.environ["EDITOR"]:
                    subprocess.run([editor, source_file], cwd=project_path, check=True)
                else:
                    match sys.platform:
                        case "win32":
                            os.startfile(source_file)
                        case "darwin":
                            subprocess.run(
                                ["open", "-t", source_file],
                                stdout=subprocess.DEVNULL,
                                check=True,
                            )
                        case _:
                            subprocess.run(
                                ["xdg-open", source_file],
                                stdout=subprocess.DEVNULL,
                                check=True,
                            )
            except Exception:
                raise RuntimeError("Unable to open an editor")
            finally:
                observer.stop()
                observer.join()

                # Kill all child processes (including the .pdf viewer processes
                # created by open_pdf()
                for child in psutil.Process(os.getpid()).children(recursive=True):
                    child.kill()

            # TODO: git handling here
            return f"Saved changes to {project_path}"
    else:
        return f"A Tewii project does not exist at {project_path}"
