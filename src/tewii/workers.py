import os
import platform
import subprocess
from pathlib import Path

import pypandoc
from watchdog.events import PatternMatchingEventHandler

from tewii.project import Project

PDFLATEX: str = "pdflatex"


def open_pdf_previewer(project: Project, base_dir: Path) -> None:
    """Opens the OS-native PDF viewer to preview the rendered project.

    Args:
        project (Project): The project whose source files will be previewed
        base_dir (Path): an ABSOLUTE path to the project directory, which
            is used to build a path to a .pdf
    """
    pdf = base_dir.resolve() / f"{project.name}.pdf"

    match platform.system():
        case "Windows":
            os.startfile(pdf)
        # Use Popen instead of run because it's non-blocking
        case "Darwin":
            subprocess.Popen(["open", pdf], stdout=subprocess.DEVNULL)
        case _:
            subprocess.Popen(["xdg-open", pdf], stdout=subprocess.DEVNULL)


class SourceFileMonitor(PatternMatchingEventHandler):
    """Monitors the source files in a project for any changes.

    If any source files have been changed, Pandoc and Pdflatex will be invoked
    to render the .md files into .tex and .pdf.

    Args:
        project (Project): The project whose source files will be monitored
        base_dir (Path): an ABSOLUTE path to the project directory, which
            is used to build absolute source file paths to monitor

    """

    project: Project
    base_dir: Path

    def __init__(self, project: Project, base_dir: Path):
        self.project = project
        # No harm in double-resolving?
        self.base_dir = base_dir.resolve()

        # Build absolute paths to pass to the observer (but as strings since
        # watchdog doesn't handle Paths)
        absolute_source_files = list(
            map(lambda file: str(base_dir / file), project.source_files)
        )
        super().__init__(
            patterns=absolute_source_files,
            ignore_directories=True,
        )

        try:
            pypandoc.get_pandoc_version()
            subprocess.run([PDFLATEX, "--version"], stdout=subprocess.DEVNULL)
        except OSError:
            raise RuntimeError(
                "Required dependencies 'pandoc' and/or 'pdflatex' are not installed"
            )

    def on_modified(self, event):
        """Handles a source file being updated.

        When a source file is updated, Pandoc and Pdflatex will be invoked to
        generate its .tex and .pdf respectively.
        """

        # TODO: currently will only handle one source file!
        # TODO: also want a proper way of keeping and logging any errors here
        tex_source_file = self.base_dir / f"{self.project.name}.tex"

        latex = pypandoc.convert_file(
            Path(str(event.src_path)),
            "tex",
            outputfile=tex_source_file,
            extra_args=["--standalone"],
        )
        subprocess.run(
            [
                PDFLATEX,
                "-interaction=nonstopmode",  # Ignore any errors in the output pdf
                f"-output-directory={self.base_dir}",
                tex_source_file,
            ],
            input=latex,
            text=True,
            stdout=subprocess.DEVNULL,
        )
