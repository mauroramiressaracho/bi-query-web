from typing import Protocol

from app.models import MetadataResponse


class DatabaseAdapter(Protocol):
    def get_metadata(self) -> MetadataResponse: ...
    def execute_select(self, sql: str, limit: int) -> tuple[list[str], list[list[object | None]]]: ...
