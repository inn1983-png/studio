import httpx
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_user_required
from src.api.schemas.provider import (
    CreateProviderRequest,
    ProviderResponse,
    UpdateProviderRequest,
)
from src.core.database import get_db
from src.core.logging import get_logger
from src.models.provider import Provider, ProviderCapability, ProviderType
from src.models.user import User

logger = get_logger(__name__)

router = APIRouter()


@router.get("/capabilities")
async def get_capabilities(
    current_user: User = Depends(get_current_user_required),
):
    return {
        "provider_types": [pt.value for pt in ProviderType],
        "capabilities": [pc.value for pc in ProviderCapability],
    }


@router.get("/", response_model=List[ProviderResponse])
async def list_providers(
    *,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    provider_type: Optional[str] = Query(None),
    capability: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    stmt = select(Provider).order_by(Provider.priority.desc()).offset(skip).limit(limit)
    if provider_type is not None:
        stmt = stmt.where(Provider.provider_type == provider_type)
    if is_active is not None:
        stmt = stmt.where(Provider.is_active == is_active)
    result = await db.execute(stmt)
    providers = result.scalars().all()
    if capability is not None:
        providers = [p for p in providers if p.capabilities and capability in p.capabilities]
    return [ProviderResponse(id=str(p.id), name=p.name, provider_type=p.provider_type, endpoint_url=p.endpoint_url, config=p.config, capabilities=p.capabilities, is_active=p.is_active, priority=p.priority, max_concurrent=p.max_concurrent, rate_limit_per_minute=p.rate_limit_per_minute, health_status=p.health_status) for p in providers]


@router.post("/", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    *,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    request: CreateProviderRequest,
):
    provider = Provider(
        name=request.name,
        provider_type=request.provider_type,
        endpoint_url=request.endpoint_url,
        api_key_encrypted=request.api_key,
        config=request.config or {},
        capabilities=request.capabilities or [],
        is_active=request.is_active,
        priority=request.priority,
        max_concurrent=request.max_concurrent,
        rate_limit_per_minute=request.rate_limit_per_minute,
        user_id=current_user.id,
    )
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    return ProviderResponse(id=str(provider.id), name=provider.name, provider_type=provider.provider_type, endpoint_url=provider.endpoint_url, config=provider.config, capabilities=provider.capabilities, is_active=provider.is_active, priority=provider.priority, max_concurrent=provider.max_concurrent, rate_limit_per_minute=provider.rate_limit_per_minute, health_status=provider.health_status)


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    *,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    provider_id: str,
):
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider不存在")
    return ProviderResponse(id=str(provider.id), name=provider.name, provider_type=provider.provider_type, endpoint_url=provider.endpoint_url, config=provider.config, capabilities=provider.capabilities, is_active=provider.is_active, priority=provider.priority, max_concurrent=provider.max_concurrent, rate_limit_per_minute=provider.rate_limit_per_minute, health_status=provider.health_status)


@router.patch("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    *,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    provider_id: str,
    request: UpdateProviderRequest,
):
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider不存在")
    update_data = request.model_dump(exclude_unset=True)
    if "api_key" in update_data:
        provider.api_key_encrypted = update_data.pop("api_key")
    for key, value in update_data.items():
        setattr(provider, key, value)
    await db.commit()
    await db.refresh(provider)
    return ProviderResponse(id=str(provider.id), name=provider.name, provider_type=provider.provider_type, endpoint_url=provider.endpoint_url, config=provider.config, capabilities=provider.capabilities, is_active=provider.is_active, priority=provider.priority, max_concurrent=provider.max_concurrent, rate_limit_per_minute=provider.rate_limit_per_minute, health_status=provider.health_status)


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    *,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    provider_id: str,
):
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider不存在")
    await db.delete(provider)
    await db.commit()


@router.post("/{provider_id}/health-check")
async def health_check_provider(
    *,
    current_user: User = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_db),
    provider_id: str,
):
    stmt = select(Provider).where(Provider.id == provider_id)
    result = await db.execute(stmt)
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider不存在")
    health_status = "unhealthy"
    if provider.endpoint_url:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(provider.endpoint_url)
                if resp.status_code < 500:
                    health_status = "healthy"
        except Exception:
            health_status = "unreachable"
    provider.health_status = health_status
    provider.last_health_check = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(provider)
    return {"provider_id": str(provider.id), "health_status": provider.health_status, "last_health_check": provider.last_health_check.isoformat() if provider.last_health_check else None}
