import os
import re
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from functions import require_authenticated_user, save_upload_file
from crud import upload_video, get_videos_by_user_id
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
    
    if not 4 <= len(title) <= 24:
        return {"error": 1}
    
    if not 5 <= len(description) <= 400:
        return {"error": 2}
    
    user_id = data["user_id"]

    if video.content_type not in ALLOWED_VIDEO_TYPES:
        return {"error": 3}

    video_bytes = await video.read()
    if len(video_bytes) > MAX_VIDEO_SIZE:
        return {"error": 4}
    await video.seek(0)

    if miniature.content_type not in ALLOWED_IMAGE_TYPES:
        return {"error": 5}
    image_bytes = await miniature.read()
    if len(image_bytes) > MAX_IMAGE_SIZE:
        return {"error": 6}
    await miniature.seek(0)
    
    video_extension = os.path.splitext(video.filename)[1]
    miniature_extension = os.path.splitext(miniature.filename)[1]
    title_hashtags = re.findall(r"#\w+", title)
    description_hashtags = re.findall(r"#\w+", description)
    hashtags = title_hashtags + description_hashtags
    video_data =  await upload_video(db=db, user_id=user_id, title=title, description=description, video_extension=video_extension, miniature_extension=miniature_extension,
                                     hashtags=hashtags)

    await save_upload_file(video, f"media/videos/{video_data.id}{video_extension}")
    await save_upload_file(miniature, f"media/miniatures/{video_data.id}{miniature_extension}")

    return {"success": "The video has been uploaded successfully!"}

@router.get("/API/my_videos")
async def get_my_videos(data=Depends(require_authenticated_user()), db: AsyncSession=Depends(get_db)):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    return await get_videos_by_user_id(db=db, user_id=user_id)