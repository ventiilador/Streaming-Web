from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import RedirectResponse, FileResponse
from crud import get_video_data_by_id, comment, get_comments, like_unlike_comment, dislike_undislike_comment, like_unlike_video, dislike_undislike_video, subscribe_by_video
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import VideoIdForm, CommentForm, GetCommentsForm, LikeComment
from functions import require_authenticated_user

router = APIRouter()

@router.get("/video")
def get_video(redirect=Depends(require_authenticated_user())):
    
    if isinstance(redirect, RedirectResponse):
        return redirect

    return FileResponse(
        "static/html/video.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@router.post("/API/video")
async def post_get_video(
    video_id: VideoIdForm = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    return await get_video_data_by_id(db=db, video_id=video_id.id, user_id=user_id)

@router.post("/API/comment")
async def post_comment(
    form_data: CommentForm = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    video_id = form_data.video_id
    content = form_data.content

    return await comment(db=db, user_id=user_id, video_id=video_id, content=content)

@router.post("/API/get_comments")
async def post_get_comments(
    form_data: GetCommentsForm = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    video_id = form_data.video_id
    offset = form_data.offset
    order_by = form_data.order_by
    user_id = data["user_id"]

    return await get_comments(db=db, user_id=user_id, video_id=video_id, offset_value=offset, order_by=order_by)


@router.post("/API/like_comment")
async def post_like_comment(
    comment_id: LikeComment = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    comment_id = comment_id.comment_id

    result = await like_unlike_comment(db=db, user_id=user_id, comment_id= comment_id)
    return {"like": result}

@router.post("/API/dislike_comment")
async def post_dislike_comment(
    comment_id: LikeComment = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    comment_id = comment_id.comment_id

    result = await dislike_undislike_comment(db=db, user_id=user_id, comment_id= comment_id)
    return {"dislike": result}

@router.post("/API/like_video")
async def post_like_video(
    video_id: VideoIdForm = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    return await like_unlike_video(db=db, user_id=user_id, video_id=video_id.id)

@router.post("/API/dislike_video")
async def post_dislike_video(
    video_id: VideoIdForm = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    return await dislike_undislike_video(db=db, user_id=user_id, video_id=video_id.id)

@router.post("/API/subscribe_by_video")
async def post_subscribe_by_video(
    video_id: VideoIdForm = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    video_id = video_id.id

    return await subscribe_by_video(db=db, user_id=user_id, video_id=video_id)
