from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

import models
from database import get_db
from schemas import CalendarEventCreate, CalendarEventResponse
from auth import CurrentUser

router = APIRouter()

@router.post("/", response_model=CalendarEventResponse)
async def create_event(
    data: CalendarEventCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    event = models.CalendarEvent(
        title=data.title,
        description=data.description,
        event_date=data.event_date
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)

    return event


@router.get("/", response_model=list[CalendarEventResponse])
async def get_events(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.CalendarEvent)
        .order_by(models.CalendarEvent.event_date)
    )

    return result.scalars().all()


@router.patch("/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    data: CalendarEventCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    result = await db.execute(
        select(models.CalendarEvent)
        .where(models.CalendarEvent.id == event_id)
    )
    event = result.scalars().first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    event.title = data.title
    event.description = data.description
    event.event_date = data.event_date

    await db.commit()
    await db.refresh(event)

    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    result = await db.execute(
        select(models.CalendarEvent)
        .where(models.CalendarEvent.id == event_id)
    )
    event = result.scalars().first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    await db.delete(event)
    await db.commit()

    return None


@router.get("/post-dates")
async def get_post_dates(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(func.date(models.Post.date_posted))
        .distinct()
        .order_by(func.date(models.Post.date_posted).desc())
    )

    return result.scalars().all()