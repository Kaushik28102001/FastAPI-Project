from typing import Annotated
from fastapi import UploadFile, HTTPException, status
from PIL import UnidentifiedImageError
from datetime import date, datetime, time
from sqlalchemy import select, func
from fastapi import HTTPException, status
from database import get_db
import schemas
from auth import CurrentUser, OptionalCurrentUser



from fastapi import APIRouter, Depends, HTTPException, Query, status, Body


from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
DBSession = Annotated[AsyncSession, Depends(get_db)]
import models
from postimage_utils import delete_post_image, process_post_image
from auth import CurrentUser
from config import settings
from database import get_db
from schemas import PaginatedPostsResponse, PostCreate, PostResponse, PostUpdate, CommentResponse, CommentCreate
from starlette.concurrency import run_in_threadpool

router = APIRouter()


@router.get("", response_model=PaginatedPostsResponse)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = settings.posts_per_page,
):

    count_result = await db.execute(
        select(func.count()).select_from(models.Post)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(
            selectinload(models.Post.author),
            selectinload(models.Post.post_likes),  # ADD THIS
        )
        .order_by(models.Post.date_posted.desc())
        .offset(skip)
        .limit(limit),
    )

    posts = result.scalars().all()

    has_more = skip + len(posts) < total

    return PaginatedPostsResponse(
        posts=[
            PostResponse.model_validate(post)
            for post in posts
        ],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    new_post = models.Post(
        title=post.title,
        short_content=post.short_content,
        content=post.content,
        image_file=None,
        user_id=current_user.id,
    )

    db.add(new_post)

    await db.commit()

    await db.refresh(
        new_post,
        attribute_names=["author"],
    )

    return new_post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id),
    )
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@router.get("/date/{selected_date}")
async def get_posts_by_date(
    selected_date: date,
    db: Annotated[AsyncSession, Depends(get_db)],
):

    start_datetime = datetime.combine(
        selected_date,
        time.min,
    )

    end_datetime = datetime.combine(
        selected_date,
        time.max,
    )

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(
            models.Post.date_posted >= start_datetime,
            models.Post.date_posted <= end_datetime,
        )
        .order_by(models.Post.date_posted.desc())
    )

    posts = result.scalars().all()

    return [
        PostResponse.model_validate(post)
        for post in posts
    ]

@router.patch(
    "/{post_id}/comments/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    post_id: int,
    comment_id: int,
    comment_data: schemas.CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    result = await db.execute(
        select(models.PostComment)
        .options(selectinload(models.PostComment.user))
        .where(
            models.PostComment.id == comment_id,
            models.PostComment.post_id == post_id,
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    # Allow if the user owns the comment OR is an admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to edit this comment",
        )

    if not comment_data.comment.strip():
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty",
        )

    comment.comment = comment_data.comment.strip()

    await db.commit()
    await db.refresh(comment, attribute_names=["user"])

    return comment


@router.delete(
    "/{post_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    result = await db.execute(
        select(models.PostComment).where(
            models.PostComment.id == comment_id,
            models.PostComment.post_id == post_id,
        )
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    # Allow if the user owns the comment OR is an admin
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this comment",
        )

    await db.delete(comment)
    await db.commit()
@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(
    post_id: int,
    post_data: PostCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    post.title = post_data.title
    post.content = post_data.content

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{post_id}/picture", response_model=PostResponse)
async def upload_post_picture(
    post_id: int,
    file: UploadFile,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this post image",
        )

    content = await file.read()

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=400,
            detail="File too large",
        )

    from postimage_utils import (
        process_post_image,
        delete_post_image,
    )

    try:
        new_filename = await run_in_threadpool(
            process_post_image,
            content,
        )
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )

    old_filename = post.image_file

    post.image_file = new_filename

    await db.commit()
    await db.refresh(post)

    if old_filename:
        delete_post_image(old_filename)

    return post


@router.get("/post-dates")
async def get_post_dates(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(
            func.date(models.Post.date_posted)
        )
        .distinct()
        .order_by(
            func.date(models.Post.date_posted).desc()
        )
    )

    return result.scalars().all()


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    await db.delete(post)
    await db.commit()


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
)
async def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    # Check post exists
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    # Prevent empty comments
    if not comment.comment.strip():
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty",
        )

    new_comment = models.PostComment(
        post_id=post_id,
        user_id=current_user.id,
        comment=comment.comment.strip(),
    )

    db.add(new_comment)

    await db.commit()
    await db.refresh(new_comment, attribute_names=["user"])   # <-- changed this line only

    return new_comment

# NOTE: Previously there were TWO handlers registered for
# POST /{post_id}/comments. The first one referenced an
# undefined variable `comment_data` (should have been `comment`),
# which raised a NameError on every request and caused the
# 500 Internal Server Error you were seeing. Since FastAPI
# matches routes in the order they were added, that broken
# handler was the one actually running — the second, working
# handler further down was unreachable dead code.
#
# This is now the single handler for that route, combining the
# `response_model` from the first version with the working logic
# and validation from the second.
@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponse],
)
async def get_comments(
    post_id: int,
    db: DBSession,
):

    result = await db.execute(
        select(models.PostComment)
        .options(selectinload(models.PostComment.user))
        .where(
            models.PostComment.post_id == post_id
        )
        .order_by(
            models.PostComment.created_at.desc()
        )
    )

    comments = result.scalars().all()

    return comments


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
)
async def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    # Check post exists
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    # Prevent empty comments
    if not comment.comment.strip():
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty",
        )

    new_comment = models.PostComment(
        post_id=post_id,
        user_id=current_user.id,
        comment=comment.comment.strip(),
    )

    db.add(new_comment)

    await db.commit()
    await db.refresh(new_comment, attribute_names=["user"])

    return new_comment


@router.get("/{post_id}/likes/count")
async def get_like_count(
    post_id: int,
    db: DBSession,
):

    result = await db.execute(
        select(
            func.count(models.PostLike.id)
        ).where(
            models.PostLike.post_id == post_id
        )
    )

    count = result.scalar()

    return {
        "post_id": post_id,
        "likes": count,
    }


@router.get("/{post_id}/likes/status")
async def get_like_status(
    post_id: int,
    db: DBSession,
    current_user: OptionalCurrentUser,
):
    count_result = await db.execute(
        select(func.count(models.PostLike.id)).where(
            models.PostLike.post_id == post_id
        )
    )
    like_count = count_result.scalar() or 0

    liked = False
    if current_user:
        result = await db.execute(
            select(models.PostLike).where(
                models.PostLike.post_id == post_id,
                models.PostLike.user_id == current_user.id,
            )
        )
        liked = result.scalars().first() is not None

    return {
        "likes": like_count,
        "liked": liked,
    }




@router.post("/{post_id}/repost")
async def toggle_repost(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    # Check post exists
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    # Check if already reposted
    result = await db.execute(
        select(models.Repost).where(
            models.Repost.post_id == post_id,
            models.Repost.user_id == current_user.id,
        )
    )

    existing_repost = result.scalars().first()

    if existing_repost:
        # Undo repost
        await db.delete(existing_repost)
        action = "unreposted"

    else:
        # Create repost
        new_repost = models.Repost(
            post_id=post_id,
            user_id=current_user.id,
        )

        db.add(new_repost)
        action = "reposted"

    await db.commit()

    # Count reposts
    count_result = await db.execute(
        select(func.count(models.Repost.id)).where(
            models.Repost.post_id == post_id
        )
    )

    repost_count = count_result.scalar() or 0

    return {
        "action": action,
        "reposts": repost_count,
    }

@router.post("/{post_id}/like")
async def toggle_like(
    post_id: int,
    db: DBSession,
    current_user: CurrentUser,
):

    # Check post exists
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )

    # Check existing like
    result = await db.execute(
        select(models.PostLike).where(
            models.PostLike.post_id == post_id,
            models.PostLike.user_id == current_user.id,
        )
    )

    existing_like = result.scalars().first()

    if existing_like:
        await db.delete(existing_like)
        action = "unliked"
    else:
        new_like = models.PostLike(
            post_id=post_id,
            user_id=current_user.id,
        )
        db.add(new_like)
        action = "liked"

    await db.commit()

    # Count likes
    count_result = await db.execute(
        select(func.count(models.PostLike.id)).where(
            models.PostLike.post_id == post_id
        )
    )

    like_count = count_result.scalar() or 0

    return {
        "action": action,
        "likes": like_count,
    }