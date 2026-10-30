import os
from json import JSONDecodeError
from pathlib import Path

from watchdog.events import (
    DirModifiedEvent,
    FileModifiedEvent,
    PatternMatchingEventHandler,
)

from tewii.conversion import convert_source_files
from tewii.project import Project


class ProjectHandler(PatternMatchingEventHandler):
    """Stores the current project's context and handles its files being edited.

    When the project's .tewii.json is edited (e.g. to include additional source
    files), the internal project state will be updated accordingly.

    When any of the project's source files are modified, they will be rerendered
    to create a new .tex and .pdf file.
    """

    project: Project
    base_dir: Path
    absolute_source_files: list[Path]
    tewii_project_file: Path

    def set_project_from_file(self):
        """Set the ProjectFileMonitor's project from the .tewii.json file, and
        also updates the absolute_source_files list.

        This method is intended to be called when first editing a project, as well
        as whenever .tewii.json is modified.

        If the .json is malformed/invalid or doesn't exist, appropriate errors
        are raised.
        """
        if self.tewii_project_file.exists():
            with open(self.tewii_project_file, "r") as file:
                try:
                    self.project = Project.from_json(file.read())
                except TypeError:
                    raise RuntimeError(
                        f"{self.tewii_project_file} is an invalid Tewii project file"
                    )
                except JSONDecodeError:
                    raise RuntimeError(
                        f"{self.tewii_project_file} contains malformed JSON"
                    )
        else:
            raise RuntimeError(
                f"{self.tewii_project_file} does not exist; has it been deleted?"
            )

        self.absolute_source_files = list(
            map(lambda file: self.base_dir / file, self.project.source_files)
        )

    def __init__(self, base_dir: Path) -> None:
        """
        Args:
            base_dir (Path): a path to the project directory, which is assumed
                to contain both the .tewii.json file and source files
        """
        self.base_dir = base_dir.resolve()
        self.tewii_project_file = self.base_dir / ".tewii.json"

        self.set_project_from_file()

        super().__init__(
            patterns=[str(self.base_dir / "*.md"), str(self.tewii_project_file)],
            ignore_directories=False,
        )

        convert_source_files(self.base_dir, self.project, self.absolute_source_files)

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        """Handle a modified file event."""
        modified_file = Path(os.fsdecode(event.src_path))

        # TODO: probably shouldn't be able to change the name while a project is open?
        if modified_file == self.tewii_project_file:
            self.set_project_from_file()

        convert_source_files(self.base_dir, self.project, self.absolute_source_files)
