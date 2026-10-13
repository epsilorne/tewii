from pathlib import Path

from watchdog.events import PatternMatchingEventHandler

from tewii.project import Project


class SourceFileMonitor(PatternMatchingEventHandler):
    """Monitors the source files in a project for any changes.

    If any source files have been changed, Pandoc and Pdflatex will be invoked
    to render the .md files into .tex and .pdf.

    Args:
        project (Project): The project whose source files will be monitored
        base_dir (Path): an ABSOLUTE path to the project directory, which
            is used to build absolute source file paths to monitor

    """

    def __init__(self, project: Project, base_dir: Path):
        # Build absolute paths to pass to the observer (but as strings since
        # watchdog doesn't handle Paths)
        absolute_source_files = list(
            map(lambda file: str(base_dir / file), project.source_files)
        )
        super().__init__(
            patterns=absolute_source_files,
            ignore_directories=True,
        )

    def on_modified(self, event):
        """Handles a source file being updated.

        When a source file is updated, Pandoc and Pdflatex will be invoked to
        generate its .tex and .pdf respectively.
        """
        # TODO: pandoc + pdflatex
        print("change")
