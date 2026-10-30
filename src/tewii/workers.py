import os
import subprocess
import sys
from pathlib import Path

import click
from notifypy import Notify
from watchdog.events import PatternMatchingEventHandler

from tewii.project import Project
from tewii.util import PANDOC, PDFLATEX


def send_notification(message: str) -> None:
    notification = Notify()
    notification.title = "Tewii"
    notification.message = message
    notification.send()


def open_pdf_previewer(project: Project, base_dir: Path) -> None:
    """Opens the OS-native PDF viewer to preview the rendered project.

    Args:
        project (Project): The project whose source files will be previewed
        base_dir (Path): an ABSOLUTE path to the project directory, which
            is used to build a path to a .pdf
    """
    pdf = base_dir.resolve() / f"{project.name}.pdf"

    match sys.platform:
        case "win32":
            os.startfile(pdf)
        # Use Popen instead of run because it's non-blocking
        case "darwin":
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

    # While the list itself isn't a list[Path], because it's constructed from a
    # list[Path] it should still be fine
    absolute_source_files: list[str]

    def convert_source_files(self) -> None:
        """Convert the project's .md source files into .tex and .pdf.

        When called, this function invokes both Pandoc and Pdflatex to parse the
        source .md files and generate .tex and .pdf in the project base directory.
        """
        tex_source_file = self.base_dir / f"{self.project.name}.tex"

        pandoc_args = (
            [PANDOC]
            + self.absolute_source_files
            + [
                "-o",
                tex_source_file,
                "--standalone",
            ]
        )

        pdflatex_args = [
            PDFLATEX,
            "-interaction=nonstopmode",
            f"-output-directory={self.base_dir}",
            tex_source_file,
        ]

        try:
            subprocess.run(pandoc_args, check=True, capture_output=True)
            subprocess.run(pdflatex_args, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            if click.get_current_context(silent=True):
                errmsg = e.stderr.decode()
                send_notification(errmsg)
                click.secho(f"Runtime Error: {errmsg}", fg="red", file=sys.stderr)

    def __init__(self, project: Project, base_dir: Path) -> None:
        self.project = project
        # No harm in double-resolving?
        self.base_dir = base_dir.resolve()

        # Build absolute paths to pass to the observer (but as strings since
        # watchdog doesn't handle Paths)
        self.absolute_source_files = list(
            map(lambda file: str(base_dir / file), project.source_files)
        )
        super().__init__(
            patterns=self.absolute_source_files,
            ignore_directories=True,
        )

        self.convert_source_files()

    def on_modified(self, event) -> None:
        """Handles a source file being updated.

        When a source file is updated, Pandoc and Pdflatex will be invoked to
        generate its .tex and .pdf respectively.
        """
        self.convert_source_files()
