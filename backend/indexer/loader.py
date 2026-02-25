import logging
from collections.abc import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.grant import Grant
from indexer.base import RawGrant, RawOrganization, RawRecord

logger = logging.getLogger(__name__)


def load_records(session: Session, records: Iterator[RawRecord]) -> dict[str, int]:
    """Load raw records into the database, upserting organizations and inserting grants.

    Returns counts of created/updated entities.
    """
    stats = {"orgs_created": 0, "orgs_updated": 0, "grants_created": 0}

    for record in records:
        for raw_org in record.organizations:
            _upsert_org(session, raw_org, stats)
        for raw_grant in record.grants:
            _insert_grant(session, raw_grant, stats)
        session.commit()

    return stats


def _upsert_org(session: Session, raw: RawOrganization, stats: dict[str, int]) -> Organization:
    stmt = select(Organization).where(
        Organization.registry == raw.registry,
        Organization.external_id == raw.external_id,
    )
    existing = session.execute(stmt).scalar_one_or_none()
    if existing:
        existing.name = raw.name
        existing.country = raw.country or existing.country
        existing.website = raw.website or existing.website
        existing.city = raw.city or existing.city
        existing.region = raw.region or existing.region
        stats["orgs_updated"] += 1
        return existing
    else:
        org = Organization(
            name=raw.name,
            registry=raw.registry,
            external_id=raw.external_id,
            country=raw.country,
            website=raw.website,
            city=raw.city,
            region=raw.region,
        )
        session.add(org)
        session.flush()
        stats["orgs_created"] += 1
        return org


def _insert_grant(session: Session, raw: RawGrant, stats: dict[str, int]) -> None:
    funder = session.execute(
        select(Organization).where(
            Organization.registry == raw.funder_registry,
            Organization.external_id == raw.funder_external_id,
        )
    ).scalar_one_or_none()
    grantee = session.execute(
        select(Organization).where(
            Organization.registry == raw.grantee_registry,
            Organization.external_id == raw.grantee_external_id,
        )
    ).scalar_one_or_none()

    if not funder or not grantee:
        logger.warning(
            "Skipping grant: funder=%s/%s grantee=%s/%s — org not found",
            raw.funder_registry, raw.funder_external_id,
            raw.grantee_registry, raw.grantee_external_id,
        )
        return

    grant = Grant(
        funder_org_id=funder.id,
        grantee_org_id=grantee.id,
        amount=raw.amount,
        year=raw.year,
        source=raw.source,
    )
    session.add(grant)
    stats["grants_created"] += 1
