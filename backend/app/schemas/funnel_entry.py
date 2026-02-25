import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.funnel_entry import FunnelStatus


class FunnelEntryCreate(BaseModel):
    org_id: uuid.UUID
    status: FunnelStatus = FunnelStatus.prospect


class FunnelEntryUpdate(BaseModel):
    status: FunnelStatus


class FunnelEntryRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    org_id: uuid.UUID
    status: FunnelStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
