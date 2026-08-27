from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas

from database import get_db
from auth import CurrentUser


router = APIRouter(
    prefix="/api/announcements",
    tags=["Announcements"]
)


# ============================================================
# GET ALL ANNOUNCEMENTS
# ============================================================

@router.get(
    "",
    response_model=list[schemas.AnnouncementResponse]
)
async def get_announcements(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Announcement)
        .order_by(models.Announcement.created_at.desc())
    )

    announcements = result.scalars().all()

    return announcements


# ============================================================
# GET ONE ANNOUNCEMENT
# ============================================================

@router.get(
    "/{announcement_id}",
    response_model=schemas.AnnouncementResponse
)
async def get_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Announcement)
        .where(models.Announcement.id == announcement_id)
    )

    announcement = result.scalar_one_or_none()

    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    return announcement


# ============================================================
# CREATE ANNOUNCEMENT
# ============================================================

@router.post(
    "",
    response_model=schemas.AnnouncementResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_announcement(
    data: schemas.AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    # ADMIN CHECK
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    announcement = models.Announcement(
        title=data.title,
        content=data.content
    )

    db.add(announcement)

    await db.commit()
    await db.refresh(announcement)

    return announcement


# ============================================================
# UPDATE ANNOUNCEMENT
# ============================================================

@router.patch(
    "/{announcement_id}",
    response_model=schemas.AnnouncementResponse
)
async def update_announcement(
    announcement_id: int,
    data: schemas.AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    result = await db.execute(
        select(models.Announcement)
        .where(models.Announcement.id == announcement_id)
    )

    announcement = result.scalar_one_or_none()

    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    # ADMIN CHECK
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if data.title is not None:
        announcement.title = data.title

    if data.content is not None:
        announcement.content = data.content

    announcement.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(announcement)

    return announcement


# ============================================================
# DELETE ANNOUNCEMENT
# ============================================================
@router.delete(
    "/{announcement_id}"
)
async def delete_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = None
):
    # ADMIN CHECK
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    result = await db.execute(
        select(models.Announcement)
        .where(models.Announcement.id == announcement_id)
    )

    announcement = result.scalar_one_or_none()

    if announcement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    await db.delete(announcement)
    await db.commit()

    return {
        "message": "Announcement deleted successfully"
    }