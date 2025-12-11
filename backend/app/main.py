from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas
from .database import SessionLocal, engine

# DB 테이블 생성 (서버 시작 시 자동 생성)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SeaRoute API", version="0.1.0")

# Dependency: 각 요청마다 DB 세션을 열고 닫음
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to SeaRoute API. Visit /docs for API documentation."}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# --- Routes API ---

@app.get("/api/routes", response_model=List[schemas.Route])
def read_routes(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = Query(None, description="노선명 또는 서비스 코드로 검색"),
    db: Session = Depends(get_db)
):
    """
    모든 노선(Route) 목록을 조회합니다.
    """
    query = db.query(models.Route)
    
    if search:
        query = query.filter(
            (models.Route.route_name.contains(search)) | 
            (models.Route.svc.contains(search))
        )
        
    routes = query.offset(skip).limit(limit).all()
    return routes

@app.get("/api/routes/{route_idx}", response_model=schemas.Route)
def read_route(route_idx: int, db: Session = Depends(get_db)):
    """
    특정 노선의 상세 정보와 기항지(Proforma) 정보를 조회합니다.
    """
    route = db.query(models.Route).filter(models.Route.route_idx == route_idx).first()
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

# --- Ports API ---

@app.get("/api/ports", response_model=List[schemas.Port])
def read_ports(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = Query(None, description="항구명 또는 코드로 검색"),
    db: Session = Depends(get_db)
):
    """
    모든 항구 목록을 조회합니다.
    """
    query = db.query(models.Port)
    
    if search:
        query = query.filter(
            (models.Port.port_name.contains(search)) | 
            (models.Port.port_code.contains(search))
        )
        
    ports = query.offset(skip).limit(limit).all()
    return ports

@app.get("/api/ports/{port_code}", response_model=schemas.Port)
def read_port(port_code: str, db: Session = Depends(get_db)):
    """
    특정 항구의 상세 정보를 조회합니다.
    """
    port = db.query(models.Port).filter(models.Port.port_code == port_code).first()
    if port is None:
        raise HTTPException(status_code=404, detail="Port not found")
    return port
