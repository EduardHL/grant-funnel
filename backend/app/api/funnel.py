import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.funnel_entry import FunnelEntry, FunnelStatus
from app.models.tenant import Tenant
from app.schemas.funnel_entry import FunnelEntryCreate, FunnelEntryRead, FunnelEntryUpdate

router = APIRouter()


async def _get_tenant(tenant_id: uuid.UUID, db: AsyncSession) -> Tenant:
    tenant = await db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.get("", response_model=list[FunnelEntryRead])
async def list_funnel_entries(
    tenant_id: uuid.UUID,
    status: FunnelStatus | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[FunnelEntry]:
    await _get_tenant(tenant_id, db)
    stmt = select(FunnelEntry).where(FunnelEntry.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(FunnelEntry.status == status)
    stmt = stmt.order_by(FunnelEntry.updated_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("", response_model=FunnelEntryRead, status_code=201)
async def create_funnel_entry(
    tenant_id: uuid.UUID,
    body: FunnelEntryCreate,
    db: AsyncSession = Depends(get_db),
) -> FunnelEntry:
    await _get_tenant(tenant_id, db)
    entry = FunnelEntry(tenant_id=tenant_id, **body.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.post("/bulk", response_model=list[FunnelEntryRead], status_code=201)
async def bulk_create_funnel_entries(
    tenant_id: uuid.UUID,
    body: list[FunnelEntryCreate],
    db: AsyncSession = Depends(get_db),
) -> list[FunnelEntry]:
    await _get_tenant(tenant_id, db)
    entries = [FunnelEntry(tenant_id=tenant_id, **item.model_dump()) for item in body]
    db.add_all(entries)
    await db.commit()
    for entry in entries:
        await db.refresh(entry)
    return entries


@router.patch("/{entry_id}", response_model=FunnelEntryRead)
async def update_funnel_entry(
    tenant_id: uuid.UUID,
    entry_id: uuid.UUID,
    body: FunnelEntryUpdate,
    db: AsyncSession = Depends(get_db),
) -> FunnelEntry:
    entry = await db.get(FunnelEntry, entry_id)
    if not entry or entry.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Funnel entry not found")
    entry.status = body.status
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_funnel_entry(
    tenant_id: uuid.UUID,
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    entry = await db.get(FunnelEntry, entry_id)
    if not entry or entry.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Funnel entry not found")
    await db.delete(entry)
    await db.commit()
