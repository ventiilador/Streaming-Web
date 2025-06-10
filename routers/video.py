from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import RedirectResponse, FileResponse
from auth import verify_token
from crud import get_video_data_by_id, comment, get_comments, like_unlike_comment, dislike_undislike_comment, like_unlike_video, dislike_undislike_video, subscribe
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
    token_data = verify_token(token=token)
    if not token_data:
        return {"Access Error": "You are not allowed to get data"}
    
    user_id = token_data["user_id"]
    return await get_video_data_by_id(db=db, video_id=video_id.id, user_id=user_id)

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

    return await get_comments(db=db, user_id=user_id, video_id=video_id, offset_value=offset, order_by=order_by)


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

    result = await like_unlike_comment(db=db, user_id=user_id, comment_id= comment_id)
    return {"like": result}

@router.post("/API/dislike_comment")
async def post_dislike_comment(request: Request, comment_id: LikeComment = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return {"Access Error": "You are not allowed to get data"}
    token_data = verify_token(token=token)
    if not token_data:
        return {"Access Error": "You are not allowed to get data"}
    
    user_id = token_data["user_id"]
    comment_id = comment_id.comment_id

    result = await dislike_undislike_comment(db=db, user_id=user_id, comment_id= comment_id)
    return {"dislike": result}

@router.post("/API/like_video")
async def post_like_video(request: Request, video_id: VideoIdForm = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return {"Access Error": "You are not allowed to get data"}
    token_data = verify_token(token=token)
    if not token_data:
        return {"Access Error": "You are not allowed to get data"}
    
    user_id = token_data["user_id"]

    return await like_unlike_video(db=db, user_id=user_id, video_id=video_id.id)

@router.post("/API/dislike_video")
async def post_dislike_video(request: Request, video_id: VideoIdForm = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return {"Access Error": "You are not allowed to get data"}
    token_data = verify_token(token=token)
    if not token_data:
        return {"Access Error": "You are not allowed to get data"}
    
    user_id = token_data["user_id"]

    return await dislike_undislike_video(db=db, user_id=user_id, video_id=video_id.id)

@router.post("/API/subscribe")
async def post_subscribe(request: Request, video_id: VideoIdForm = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return {"Access Error": "You are not allowed to get data"}
    token_data = verify_token(token=token)
    if not token_data:
        return {"Access Error": "You are not allowed to get data"}
    
    user_id = token_data["user_id"]
    video_id = video_id.id

    return await subscribe(db=db, user_id=user_id, video_id=video_id)