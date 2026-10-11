import json
from dataclasses import asdict, dataclass, field


@dataclass
class Project:
    """
    Stores information about a project.

    Attributes:
        name (str): The name of the project.
        source_files (list[str]): A list of source files that Pandoc converts
            into LaTeX. The first file in the list is also the one opened
            when the project is edited.
    """
    name: str
    source_files: list[str] = field(default_factory=lambda: ["document.md"])

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)

    @staticmethod
    def from_json(data: str) -> Project:
        return Project(**json.loads(data))
