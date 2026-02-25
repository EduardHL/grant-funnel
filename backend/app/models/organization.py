from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKey


class Organization(UUIDPrimaryKey, TimestampMixin, Base):
    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("registry", "external_id", name="uq_org_registry_external_id"),)

    name: Mapped[str]
    country: Mapped[Optional[str]]
    registry: Mapped[Optional[str]]
    external_id: Mapped[Optional[str]]
    website: Mapped[Optional[str]]
    city: Mapped[Optional[str]]
    region: Mapped[Optional[str]]

    grants_given: Mapped[list["Grant"]] = relationship(  # noqa: F821
        back_populates="funder", foreign_keys="Grant.funder_org_id"
    )
    grants_received: Mapped[list["Grant"]] = relationship(  # noqa: F821
        back_populates="grantee", foreign_keys="Grant.grantee_org_id"
    )
