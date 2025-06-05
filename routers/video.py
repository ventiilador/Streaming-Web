from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import RedirectResponse, FileResponse
from auth import verify_token
from crud import get_video_data_by_id, comment, get_comments_by_likes, get_comments_by_recent, get_comments_by_old, like_unlike
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import VideoIdForm, CommentForm, GetCommentsForm, LikeComment

router = APIRouter()

@router.get("/video")
def get_video(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        return RedirectResponse("/login", status_code=302)
    if not verify_token(token=token):
        return RedirectResponse("/login", status_code=302)
    return FileResponse("static/html/video.html")

@router.post("/API/video")
async def post_get_video(request: Request, video_id: VideoIdForm = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return {"Access Error": "You are not allowed to get data"}
    if not verify_token(token=token):
        return {"Access Error": "You are not allowed to get data"}
    
    return await get_video_data_by_id(db=db, video_id=video_id.id)

@router.post("/API/comment")
async def post_comment(request: Request, form_data: CommentForm = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return {"Access Error": "You are not allowed to comment"}
    token_data = verify_token(token=token)
    if not token_data:
        return {"Access Error": "You are not allowed to comment"}
    
    user_id = token_data["user_id"]
    video_id = form_data.video_id
    content = form_data.content

    return await comment(db=db, user_id=user_id, video_id=video_id, content=content)

@router.post("/API/get_comments")
async def post_get_comments(request: Request, form_data: GetCommentsForm = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return {"Access Error": "You are not allowed to get data"}
    token_data = verify_token(token=token)
    if not token_data:
        return {"Access Error": "You are not allowed to get data"}
    
    video_id = form_data.video_id
    offset = form_data.offset
    order_by = form_data.order_by
    user_id = token_data["user_id"]

    if order_by == "relevant":
        return await get_comments_by_likes(db=db, user_id=user_id, video_id=video_id, offeset_value=offset)
    elif order_by == "recent":
        return await get_comments_by_recent(db=db, user_id=user_id, video_id=video_id, offeset_value=offset)
    elif order_by == "old":
        return await get_comments_by_old(db=db, user_id=user_id, video_id=video_id, offeset_value=offset)
    return {"Error": "Incorrect Filter"}

@router.post("/API/like_comment")
async def post_like_comment(request: Request, comment_id: LikeComment = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return {"Access Error": "You are not allowed to get data"}
    token_data = verify_token(token=token)
    if not token_data:
        return {"Access Error": "You are not allowed to get data"}
    
    user_id = token_data["user_id"]
    comment_id = comment_id.comment_id

    result = await like_unlike(db=db, user_id=user_id, comment_id= comment_id)
    return {"like": result}