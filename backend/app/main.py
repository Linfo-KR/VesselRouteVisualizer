from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

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

# --- Services API ---

@app.get("/api/services", response_model=List[schemas.Service])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    모든 서비스(항로) 목록을 조회합니다.
    """
    services = db.query(models.Service).offset(skip).limit(limit).all()
    return services

@app.get("/api/services/{service_id}", response_model=schemas.Service)
def read_service(service_id: int, db: Session = Depends(get_db)):
    """
    특정 서비스의 상세 정보와 기항지(Rotation) 정보를 조회합니다.
    """
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

# --- Ports API ---

@app.get("/api/ports", response_model=List[schemas.Port])
def read_ports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    모든 항구 목록을 조회합니다.
    """
    ports = db.query(models.Port).offset(skip).limit(limit).all()
    return ports