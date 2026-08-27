from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

from auth import CurrentUser,OptionalCurrentUser


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/admin/announcements")
async def admin_announcements(
    request: Request,
    current_user: CurrentUser
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return templates.TemplateResponse(
        request=request,
        name="admin_announcements.html",
        context={
            "current_user": current_user
        }
    )


@router.get("/announcements")
async def announcements_page(
    request: Request,
    current_user: OptionalCurrentUser
):
    return templates.TemplateResponse(
        request=request,
        name="announcements.html",
        context={
            "current_user": current_user
        }
    )