"""Seed the database with sample data for development."""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Base, Organization, Grant, Tenant, FunnelEntry, FunnelStatus


def seed() -> None:
    engine = create_engine(settings.database_url_sync)

    with Session(engine) as session:
        # Check if data already exists
        if session.query(Organization).first():
            print("Database already has data. Skipping seed.")
            return

        # Sample organizations
        orgs = [
            Organization(
                name="Gates Foundation",
                registry="IRS",
                external_id="562618866",
                country="US",
                city="Seattle",
                region="WA",
                website="https://www.gatesfoundation.org",
            ),
            Organization(
                name="Ford Foundation",
                registry="IRS",
                external_id="131684331",
                country="US",
                city="New York",
                region="NY",
                website="https://www.fordfoundation.org",
            ),
            Organization(
                name="Open Society Foundations",
                registry="IRS",
                external_id="137029285",
                country="US",
                city="New York",
                region="NY",
            ),
            Organization(
                name="Doctors Without Borders",
                registry="IRS",
                external_id="133433452",
                country="US",
                city="New York",
                region="NY",
            ),
            Organization(
                name="Electronic Frontier Foundation",
                registry="IRS",
                external_id="043091431",
                country="US",
                city="San Francisco",
                region="CA",
            ),
            Organization(
                name="Khan Academy",
                registry="IRS",
                external_id="261544963",
                country="US",
                city="Mountain View",
                region="CA",
            ),
            Organization(
                name="Wikipedia Foundation",
                registry="IRS",
                external_id="200049703",
                country="US",
                city="San Francisco",
                region="CA",
            ),
            Organization(
                name="Habitat for Humanity",
                registry="IRS",
                external_id="912167934",
                country="US",
                city="Atlanta",
                region="GA",
            ),
        ]
        session.add_all(orgs)
        session.flush()

        # Sample grants (some funders giving to grantees)
        grants = [
            Grant(funder_org_id=orgs[0].id, grantee_org_id=orgs[5].id, amount=Decimal("15000000"), year=2023, source="seed"),
            Grant(funder_org_id=orgs[0].id, grantee_org_id=orgs[3].id, amount=Decimal("5000000"), year=2023, source="seed"),
            Grant(funder_org_id=orgs[0].id, grantee_org_id=orgs[7].id, amount=Decimal("2000000"), year=2022, source="seed"),
            Grant(funder_org_id=orgs[1].id, grantee_org_id=orgs[4].id, amount=Decimal("500000"), year=2023, source="seed"),
            Grant(funder_org_id=orgs[1].id, grantee_org_id=orgs[6].id, amount=Decimal("1000000"), year=2023, source="seed"),
            Grant(funder_org_id=orgs[2].id, grantee_org_id=orgs[4].id, amount=Decimal("750000"), year=2023, source="seed"),
            Grant(funder_org_id=orgs[2].id, grantee_org_id=orgs[3].id, amount=Decimal("3000000"), year=2022, source="seed"),
        ]
        session.add_all(grants)
        session.flush()

        # Sample tenant
        tenant = Tenant(name="Demo Foundation", slug="demo-foundation")
        session.add(tenant)
        session.flush()

        # Sample funnel entries
        funnel_entries = [
            FunnelEntry(tenant_id=tenant.id, org_id=orgs[3].id, status=FunnelStatus.prospect),
            FunnelEntry(tenant_id=tenant.id, org_id=orgs[4].id, status=FunnelStatus.shortlisted),
            FunnelEntry(tenant_id=tenant.id, org_id=orgs[5].id, status=FunnelStatus.researching),
            FunnelEntry(tenant_id=tenant.id, org_id=orgs[6].id, status=FunnelStatus.prospect),
            FunnelEntry(tenant_id=tenant.id, org_id=orgs[7].id, status=FunnelStatus.funded),
        ]
        session.add_all(funnel_entries)

        session.commit()
        print(f"Seeded {len(orgs)} organizations, {len(grants)} grants, 1 tenant, {len(funnel_entries)} funnel entries.")


if __name__ == "__main__":
    seed()
