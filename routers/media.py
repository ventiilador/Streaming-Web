from fastapi import APIRouter, Depends, Request, Response, Header
from fastapi.responses import FileResponse, RedirectResponse
from functions import require_authenticated_user
from pathlib import Path as SysPath

router = APIRouter()

@router.get("/profile_picture/{user_id}")
def get_profile_picture(user_id: int, redirect=Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    image_path = SysPath(f"media/profiles/{user_id}.jpg")

    if not image_path.exists():
        image_path = SysPath("media/profiles/default.jpg")
    
    return FileResponse(image_path, media_type="image/jpeg")


@router.get("/video_miniature/{video_id}")
def get_miniature(video_id: int, redirect=Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    image_path = SysPath(f"media/miniatures/{video_id}.jpg")

    return FileResponse(image_path, media_type="image/jpeg")


@router.get("/video_stream/{video_id}")
def stream_video(
    video_id: int,
    request: Request,
    redirect=Depends(require_authenticated_user()),
    range: str = Header(None)
):
    if isinstance(redirect, RedirectResponse):
        return redirect

    video_path = SysPath(f"media/videos/{video_id}.mp4")

    if not video_path.exists():
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
        "Content-Type": "video/mp4",
        "Cache-Control": "no-store"
    }

    return Response(content=data, status_code=206, headers=headers)