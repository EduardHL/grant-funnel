import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TenantCreate(BaseModel):
    name: str
    slug: str
    linked_org_id: Optional[uuid.UUID] = None


class TenantRead(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    linked_org_id: Optional[uuid.UUID]
    created_at: datetime

    model_config = {"from_attributes": True}
