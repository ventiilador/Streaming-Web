from fastapi import APIRouter, Depends, Request, Response, Header
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud import get_user_profile_extension, stream_video_permission
from functions import require_authenticated_user
from pathlib import Path as SysPath

router = APIRouter()

EXTENSION_TO_MEDIA_TYPE = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp"
}

@router.get("/profile_picture/{user_id}")
async def get_profile_picture(user_id: int, redirect=Depends(require_authenticated_user()), db: AsyncSession=Depends(get_db)):

    if isinstance(redirect, RedirectResponse):
        return redirect

    extension = await get_user_profile_extension(db=db, user_id=user_id)
    image_path = SysPath(f"media/profiles/{user_id}{extension}")

    if not image_path.exists():
        image_path = SysPath("media/profiles/default.jpg")
        media_type = "image/jpeg"
    else:
        media_type = EXTENSION_TO_MEDIA_TYPE.get(extension.lower(), "application/octet-stream")

    return FileResponse(image_path, media_type=media_type)


@router.get("/video_miniature/{video_id}")
def get_miniature(video_id: int, redirect=Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    allowed_extensions = ["jpg", "jpeg", "png", "webp"]

    image_path = None
    found_ext = None

    for ext in allowed_extensions:
        candidate = SysPath(f"media/miniatures/{video_id}.{ext}")
        if candidate.exists():
            image_path = candidate
            found_ext = ext
            break

    if not image_path:
        image_path = SysPath("media/miniatures/default.png")
        found_ext = "png"
    
    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp"
    }

    return FileResponse(image_path, media_type=mime_types.get(found_ext, "application/octet-stream"))


@router.get("/video_stream/{video_id}")
async def stream_video(
    video_id: int,
    request: Request,
    data=Depends(require_authenticated_user()),
    range: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    allowed = await stream_video_permission(db=db, user_id=user_id, video_id=video_id)

    if not allowed:
        return {"error": "Not allowed to watch this content"}

    ALLOWED_VIDEO_TYPES = {
        "video/mp4", "video/quicktime", "video/x-matroska",
        "video/x-msvideo", "video/webm"
    }
    mime_to_extensions = {
        "video/mp4": ["mp4"],
        "video/quicktime": ["mov"],
        "video/x-matroska": ["mkv"],
        "video/x-msvideo": ["avi"],
        "video/webm": ["webm"]
    }

    video_path = None
    found_ext = None
    found_mime = None

    for mime_type in ALLOWED_VIDEO_TYPES:
        for ext in mime_to_extensions[mime_type]:
            candidate = SysPath(f"media/videos/{video_id}.{ext}")
            if candidate.exists():
                video_path = candidate
                found_ext = ext
                found_mime = mime_type
                break
        if video_path:
            break

    if not video_path:
        return Response(status_code=404, content="Video no encontrado")

    file_size = video_path.stat().st_size
    start = 0
    end = file_size - 1

    if range:
        bytes_range = range.strip().lower().replace("bytes=", "")
        if "-" in bytes_range:
            start_str, end_str = bytes_range.split("-")
            if start_str.strip():
                start = int(start_str)
            if end_str.strip():
                end = int(end_str)

    chunk_size = (end - start) + 1
    with open(video_path, "rb") as video_file:
        video_file.seek(start)
        data = video_file.read(chunk_size)

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
        "Content-Type": found_mime or "application/octet-stream",
        "Cache-Control": "no-store"
    }

    return Response(content=data, status_code=206, headers=headers)
