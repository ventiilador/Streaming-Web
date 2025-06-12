import os
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse, FileResponse
from functions import require_authenticated_user, save_upload_file
from crud import upload_video
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter()

MAX_VIDEO_SIZE = 10 * 1024 * 1024 * 1024
MAX_IMAGE_SIZE = 200 * 1024 * 1024

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-matroska", "video/x-msvideo", "video/webm"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.get("/dashboard")
def get_dashboard(redirect = Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    return FileResponse(
        "static/html/dashboard.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
    })

@router.post("/API/upload_video")
async def post_upload_video(
    title: str = Form(...),
    description: str = Form(...),
    video: UploadFile = File(...),
    miniature: UploadFile = File(...),
    data=Depends(require_authenticated_user()),
    db: AsyncSession = Depends(get_db)):
    
    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    if video.content_type not in ALLOWED_VIDEO_TYPES:
        return {"error": 1}

    video_bytes = await video.read()
    if len(video_bytes) > MAX_VIDEO_SIZE:
        return {"error": 2}
    await video.seek(0)

    if miniature.content_type not in ALLOWED_IMAGE_TYPES:
        return {"error": 3}
    image_bytes = await miniature.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        return {"error": 4}
    await miniature.seek(0)
    
    video_extension = os.path.splitext(video.filename)[1]
    miniature_extension = os.path.splitext(miniature.filename)[1]
    video_data =  await upload_video(db=db, user_id=user_id, title=title, description=description, video_extension=video_extension, miniature_extension=miniature_extension)

    await save_upload_file(video, f"media/videos/{video_data.id}{video_extension}")
    await save_upload_file(miniature, f"media/miniatures/{video_data.id}{miniature_extension}")

    return {"success": "The video has been uploaded successfully!"}