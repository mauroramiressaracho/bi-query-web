from app.demo_data import get_demo_metadata
from app.models import MetadataResponse


class DemoAdapter:
    def get_metadata(self) -> MetadataResponse:
        return get_demo_metadata()

    def execute_select(self, sql: str, limit: int):
        columns = ["EMP_COD", "CHAPA", "NOME", "ORGAO"]
        rows = [
            [1, "000123", "JOÃO DA SILVA", "RECURSOS HUMANOS"],
            [1, "000124", "MARIA SOUZA", "TECNOLOGIA"],
        ]
        return columns, rows[:limit]
