from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.factory import get_adapter
from app.models import (
    ExecuteRequest,
    ExecuteResponse,
    MetadataResponse,
    QueryRequest,
    QueryResponse,
)
from app.query_builder import build_query

app = FastAPI(title="BI Query Web API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "engine": settings.db_engine}


@app.get("/api/metadata", response_model=MetadataResponse)
def metadata():
    try:
        return get_adapter().get_metadata()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/query/generate", response_model=QueryResponse)
def generate_query(request: QueryRequest):
    try:
        md = get_adapter().get_metadata()
        return QueryResponse(sql=build_query(request, md))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/query/execute", response_model=ExecuteResponse)
def execute_query(request: ExecuteRequest):
    try:
        limit = max(1, min(request.limit, settings.max_query_rows))
        columns, rows = get_adapter().execute_select(request.sql, limit)
        return ExecuteResponse(columns=columns, rows=rows)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
