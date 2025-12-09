from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Port(Base):
    """
    항구 정보를 저장하는 테이블
    """
    __tablename__ = "ports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, unique=True, nullable=True) # UN/LOCODE 등
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    # Rotation과의 관계 설정 (필요 시 추가)
    # rotations = relationship("Rotation", back_populates="port")

class Service(Base):
    """
    서비스(항로) 정보를 저장하는 테이블
    (예: 'KSH', 'PVS' 등 서비스 코드와 이름)
    """
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # 서비스 코드 (예: KSH)
    description = Column(String, nullable=True) # 서비스 전체 이름 또는 설명
    
    # Rotation과의  관계 설정
    rotations = relationship("Rotation", back_populates="service")

class Rotation(Base):
    """
    각 서비스의 기항지 순서 및 상세 정보를 저장하는 테이블
    """
    __tablename__ = "rotations"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    port_id = Column(Integer, ForeignKey("ports.id"), nullable=False)
    
    port_order = Column(Integer, nullable=False) # 기항 순서 (1, 2, 3...)
    direction = Column(String, nullable=True) # 운항 방향 (E/W/S/N)
    day = Column(Integer, nullable=True)# 입항 요일 등
    terminal = Column(String, nullable=True) # 터미널 정보

    # 관계 설정
    service = relationship("Service", back_populates="rotations")
    port = relationship("Port")
