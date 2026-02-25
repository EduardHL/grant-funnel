import enum
import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKey


class FunnelStatus(str, enum.Enum):
    prospect = "prospect"
    shortlisted = "shortlisted"
    researching = "researching"
    application_in_progress = "application_in_progress"
    funded = "funded"
    passed = "passed"


class FunnelEntry(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "funnel_entries"
    __table_args__ = (UniqueConstraint("tenant_id", "org_id", name="uq_funnel_tenant_org"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"))
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))
    status: Mapped[FunnelStatus] = mapped_column(default=FunnelStatus.prospect)

    tenant: Mapped["Tenant"] = relationship(back_populates="funnel_entries")  # noqa: F821
    organization: Mapped["Organization"] = relationship()  # noqa: F821
