from fastapi import APIRouter, HTTPException, Header
from app.config import settings
from app.ingestion.indexer import Indexer
import os

router = APIRouter()
indexer = Indexer()

def verify_admin(x_admin_key: str = Header(...)):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid Admin Key")

@router.post("/ingest/rebuild")
def rebuild_index(force: bool = False, x_admin_key: str = Header(...)):
    verify_admin(x_admin_key)
    result = indexer.rebuild(force=force)
    return result

@router.get("/sources")
def get_sources(x_admin_key: str = Header(...)):
    verify_admin(x_admin_key)
    try:
        j_count = indexer.jira_collection.count()
        c_count = indexer.code_collection.count()
    except:
        j_count, c_count = 0, 0
    return {"jira_chunks": j_count, "code_chunks": c_count}
