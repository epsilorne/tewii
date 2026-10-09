import json
from dataclasses import dataclass, asdict


@dataclass
class Project:
    name: str
    source_files: list[str]

    def __init__(self, name: str, source_files: list[str] = ["document.md"]) -> None:
        self.name = name
        self.source_files = source_files

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)

    @staticmethod
    def from_json(data: str) -> Project:
        return Project(**json.loads(data))
