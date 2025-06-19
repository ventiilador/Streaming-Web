import os
from typing import Optional
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse, FileResponse
from functions import require_authenticated_user, save_upload_file
from schemas import VideoIdForm, EditVideoForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud import check_if_user_is_video_owner_by_id, get_video_data_by_id, edit_video

router = APIRouter()

MAX_IMAGE_SIZE = 200 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.get("/edit_video")
def get_edit_video(data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse): 
        return data
    
    return FileResponse(
        "static/html/editVideo.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
    })

@router.post("/API/get_video_edit_form")
async def post_get_video_data(video_id: VideoIdForm = Body(...), db: AsyncSession = Depends(get_db), data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    isowner = await check_if_user_is_video_owner_by_id(db=db, user_id=user_id, video_id=video_id.id)

    if not isowner:
        return {"error": "You are not the video owner"}
    
    return await get_video_data_by_id(db=db, video_id=video_id.id, user_id=user_id)

@router.post("/edit_video")
async def post_edit_video(
    form: EditVideoForm = Depends(EditVideoForm.as_form),
    miniature: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())
):
    if isinstance(data, RedirectResponse):
        return data

    miniature_extension = None

    if miniature and miniature.filename:
        if miniature.content_type not in ALLOWED_IMAGE_TYPES:
            return RedirectResponse(f"/edit_video?id={form.id}&error=3", status_code=302)
        
        image_bytes = await miniature.read()
        if len(image_bytes) > MAX_IMAGE_SIZE:
            return RedirectResponse(f"/edit_video?id={form.id}&error=4", status_code=302)
        
        await miniature.seek(0)
        miniature_extension = os.path.splitext(miniature.filename)[1]

        await save_upload_file(miniature, f"media/miniatures/{form.id}{miniature_extension}")

    user_id = data["user_id"]

    result = await edit_video(
        db=db,
        user_id=user_id,
        video_id=form.id,
        title=form.title,
        description=form.description,
        miniature_extension=miniature_extension
    )

    if result:
        return RedirectResponse("/dashboard", status_code=302)