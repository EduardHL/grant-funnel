import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.grant import Grant
from app.schemas.grant import GrantCreate, GrantRead

router = APIRouter()


@router.get("", response_model=list[GrantRead])
async def list_grants(
    funder_org_id: uuid.UUID | None = None,
    grantee_org_id: uuid.UUID | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[Grant]:
    stmt = select(Grant)
    if funder_org_id:
        stmt = stmt.where(Grant.funder_org_id == funder_org_id)
    if grantee_org_id:
        stmt = stmt.where(Grant.grantee_org_id == grantee_org_id)
    stmt = stmt.order_by(Grant.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{grant_id}", response_model=GrantRead)
async def get_grant(
    grant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Grant:
    grant = await db.get(Grant, grant_id)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant


@router.post("", response_model=GrantRead, status_code=201)
async def create_grant(
    body: GrantCreate,
    db: AsyncSession = Depends(get_db),
) -> Grant:
    grant = Grant(**body.model_dump())
    db.add(grant)
    await db.commit()
    await db.refresh(grant)
    return grant


@router.delete("/{grant_id}", status_code=204)
async def delete_grant(
    grant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    grant = await db.get(Grant, grant_id)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    await db.delete(grant)
    await db.commit()
