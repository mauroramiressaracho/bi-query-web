from app.config import settings
from .demo import DemoAdapter
from .oracle import OracleAdapter
from .sqlserver import SqlServerAdapter


def get_adapter():
    engine = settings.db_engine.lower().strip()
    if engine == "oracle":
        return OracleAdapter()
    if engine in {"sqlserver", "mssql"}:
        return SqlServerAdapter()
    return DemoAdapter()
