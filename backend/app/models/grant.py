import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Index, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKey


class Grant(UUIDPrimaryKey, Base):
    __tablename__ = "grants"
    __table_args__ = (
        Index("ix_grants_funder", "funder_org_id"),
        Index("ix_grants_grantee", "grantee_org_id"),
        Index("ix_grants_funder_grantee", "funder_org_id", "grantee_org_id"),
    )

    funder_org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))
    grantee_org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    year: Mapped[Optional[int]]
    source: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    funder: Mapped["Organization"] = relationship(  # noqa: F821
        back_populates="grants_given", foreign_keys=[funder_org_id]
    )
    grantee: Mapped["Organization"] = relationship(  # noqa: F821
        back_populates="grants_received", foreign_keys=[grantee_org_id]
    )
