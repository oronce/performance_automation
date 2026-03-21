"""
CACHED_DB — Standalone FastAPI server
Exposes the DuckDB SQL client API and browser UI.

Run
---
    python app.py
    uvicorn app:app --host 0.0.0.0 --port 8002 --reload

Endpoints (all under /duck)
----------------------------
    GET  /duck/ui                        → Browser SQL client
    GET  /duck/tables                    → List tables + row counts
    GET  /duck/tables/{table}/schema     → Column names & types
    GET  /duck/tables/{table}/data       → Paginated rows
    POST /duck/query                     → Execute arbitrary SQL (read-only)

Docs
----
    http://localhost:8002/docs
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from duck_client.router import router as duck_router

app = FastAPI(
    title="CACHED_DB API",
    description="Read-only DuckDB cache — SQL client + REST access.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(duck_router)


@app.get("/health", tags=["Health"])
def health():
    """Quick liveness check."""
    from cache_builder.config import DUCKDB_PATH
    return {
        "status": "ok",
        "duckdb": DUCKDB_PATH,
        "exists": os.path.exists(DUCKDB_PATH),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=False)
