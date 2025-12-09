from pydantic import BaseModel
from typing import List, Optional

# Port Schemas
class PortBase(BaseModel):
    name: str
    code: Optional[str] = None
    lat: float
    lon: float

class PortCreate(PortBase):
    pass

class Port(PortBase):
    id: int

    class Config:
        from_attributes = True

# Rotation Schemas
class RotationBase(BaseModel):
    port_order: int
    direction: Optional[str] = None
    day: Optional[int] = None
    terminal: Optional[str] = None
    port_id: int

class RotationCreate(RotationBase):
    pass

class Rotation(RotationBase):
    id: int
    port: Port # Nested Port information

    class Config:
        from_attributes = True

# Service Schemas
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: int
    rotations: List[Rotation] = []

    class Config:
        from_attributes = True
