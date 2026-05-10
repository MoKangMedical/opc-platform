"""
OPC Platform - 同步中心路由 (from opc-sync-hub)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.sync_hub import SyncEngine
from app.services.health_checker import HealthChecker
import os

router = APIRouter(prefix="/api/sync", tags=["Sync Hub"])

SYNC_CONFIG = {
    "projects_dir": os.path.expanduser("~/Desktop/OPC"),
    "health": {"max_repo_size_gb": 20, "max_dirty_days": 7},
}


@router.get("/health")
def get_health():
    """获取仓库健康状态摘要"""
    try:
        checker = HealthChecker(SYNC_CONFIG)
        report = checker.check()
        return {"status": "ok", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/status")
def get_sync_status():
    """获取同步状态"""
    try:
        engine = SyncEngine(SYNC_CONFIG)
        status = engine.get_last_status()
        return {"status": "ok", "sync_status": status}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/run")
def run_sync():
    """手动触发同步"""
    try:
        engine = SyncEngine(SYNC_CONFIG)
        result = engine.run()
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
