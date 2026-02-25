import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    country: Optional[str] = None
    registry: Optional[str] = None
    external_id: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    registry: Optional[str] = None
    external_id: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None


class OrganizationRead(BaseModel):
    id: uuid.UUID
    name: str
    country: Optional[str]
    registry: Optional[str]
    external_id: Optional[str]
    website: Optional[str]
    city: Optional[str]
    region: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
