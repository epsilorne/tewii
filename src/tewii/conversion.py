import os
import subprocess
import sys
from pathlib import Path

import click
from notifypy import Notify

from tewii.project import Project
from tewii.util import OUTPUT_DIR, PANDOC, PDFLATEX


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
    pdf = base_dir.resolve() / OUTPUT_DIR / f"{project.name}.pdf"

    match sys.platform:
        case "win32":
            os.startfile(pdf)
        # Use Popen instead of run because it's non-blocking
        case "darwin":
            subprocess.Popen(["open", pdf], stdout=subprocess.DEVNULL)
        case _:
            subprocess.Popen(["xdg-open", pdf], stdout=subprocess.DEVNULL)


def convert_source_files(
    base_dir: Path, project: Project, absolute_source_files: list[Path]
) -> None:
    """Convert the project's .md source files into .tex and .pdf.

    When called, this function invokes both Pandoc and Pdflatex to parse the
    source .md files and generate .tex and .pdf in the project base directory.

    Args:
        base_dir (Path):
        project (Project):
        absolute_source_files (list[Path]):
    """
    tex_source_file = base_dir / OUTPUT_DIR / f"{project.name}.tex"

    pandoc_args = (
        [PANDOC]
        + absolute_source_files
        + [
            "-o",
            tex_source_file,
            "--standalone",
        ]
    )

    pdflatex_args = [
        PDFLATEX,
        "-interaction=nonstopmode",
        f"-output-directory={base_dir / OUTPUT_DIR}",
        tex_source_file,
    ]

    try:
        subprocess.run(pandoc_args, check=True, capture_output=True)
        subprocess.run(pdflatex_args, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        # TODO: doesn't seem to always work as expected; only pops up when saving
        # file and re-opening, not when you edit a file to be incorrect
        if click.get_current_context(silent=True):
            errmsg = e.stderr.decode()
            send_notification(errmsg)
            click.secho(f"Runtime Error: {errmsg}", fg="red", file=sys.stderr)
