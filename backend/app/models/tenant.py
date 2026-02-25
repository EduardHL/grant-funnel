import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKey


class Tenant(UUIDPrimaryKey, Base):
    __tablename__ = "tenants"

    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    linked_org_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    linked_org: Mapped[Optional["Organization"]] = relationship(foreign_keys=[linked_org_id])  # noqa: F821
    funnel_entries: Mapped[list["FunnelEntry"]] = relationship(back_populates="tenant")  # noqa: F821
