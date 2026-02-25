import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class GrantCreate(BaseModel):
    funder_org_id: uuid.UUID
    grantee_org_id: uuid.UUID
    amount: Optional[Decimal] = None
    year: Optional[int] = None
    source: Optional[str] = None


class GrantRead(BaseModel):
    id: uuid.UUID
    funder_org_id: uuid.UUID
    grantee_org_id: uuid.UUID
    amount: Optional[Decimal]
    year: Optional[int]
    source: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
