from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import RedirectResponse, FileResponse
from crud import get_profile_data_by_username, subscribe_by_username
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import UsernameForm
from functions import require_authenticated_user

router = APIRouter()

@router.get("/profile")
def get_profile(redirect=Depends(require_authenticated_user())):
    
    if isinstance(redirect, RedirectResponse):
        return redirect

    return FileResponse(
        "static/html/profile.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@router.post("/API/profile")
async def post_get_profile_data(
    username: UsernameForm = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    profile_data = await get_profile_data_by_username(db=db, user_id=user_id, username=username.username)
    return profile_data

@router.post("/API/subscribe_by_user")
async def post_subscribe_by_user(
    username: UsernameForm = Body(...),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())):

    if isinstance(data, RedirectResponse):
        return data

    user_id = data["user_id"]

    return await subscribe_by_username(db=db, user_id=user_id, username=username.username)
