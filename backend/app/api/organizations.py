import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate

router = APIRouter()


@router.get("", response_model=list[OrganizationRead])
async def list_organizations(
    q: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[Organization]:
    stmt = select(Organization)
    if q:
        stmt = stmt.where(Organization.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Organization.name).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/count")
async def count_organizations(
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    stmt = select(func.count()).select_from(Organization)
    if q:
        stmt = stmt.where(Organization.name.ilike(f"%{q}%"))
    result = await db.execute(stmt)
    return {"count": result.scalar_one()}


@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.post("", response_model=OrganizationRead, status_code=201)
async def create_organization(
    body: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    org = Organization(**body.model_dump())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.patch("/{org_id}", response_model=OrganizationRead)
async def update_organization(
    org_id: uuid.UUID,
    body: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    await db.commit()
    await db.refresh(org)
    return org


@router.delete("/{org_id}", status_code=204)
async def delete_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    await db.delete(org)
    await db.commit()
