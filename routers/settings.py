import os
from typing import Optional
from fastapi import APIRouter, Depends, Form, UploadFile
from fastapi.responses import RedirectResponse, FileResponse
from functions import require_authenticated_user, save_upload_file
from crud import get_profile_data_by_id, update_profile_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import UpdateProfileForm


router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
MAX_IMAGE_SIZE = 100 * 1024 * 1024

@router.get("/settings")
def get_settings(redirect=Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    return FileResponse(
        "static/html/settings.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
    })

@router.get("/profile_data")
async def get_profile_data(db: AsyncSession=Depends(get_db), data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    return await get_profile_data_by_id(db=db, user_id=user_id)

@router.post("/update_profile")
async def post_update_profile(
    form: UpdateProfileForm = Depends(UpdateProfileForm.as_form),
    profile_picture: Optional[UploadFile] = Form(None),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())
    ):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    extension = None
    print(profile_picture)
    if profile_picture:
        print("YEYEYYE")
        if profile_picture.content_type not in ALLOWED_IMAGE_TYPES:
            return {"error": "Invalid image type"}
        image_bytes = await profile_picture.read()
        if len(image_bytes) > MAX_IMAGE_SIZE:
            return {"error": "Image too large"}
        await profile_picture.seek(0)

        filename = profile_picture.filename
        extension = os.path.splitext(filename)[1]

        await save_upload_file(profile_picture, f"media/profiles/{user_id}{extension}")

    return await update_profile_by_id(db=db, user_id=user_id, username=form.username, biography=form.biography, profile_extension=extension)