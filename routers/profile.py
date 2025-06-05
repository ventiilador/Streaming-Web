from fastapi import APIRouter, Request, Depends, Body
from fastapi.responses import RedirectResponse, FileResponse
from auth import verify_token
from crud import get_profile_data_by_username
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import UsernameForm

router = APIRouter()

@router.get("/profile")
def get_profile(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        return RedirectResponse("/login", status_code=302)
    if not verify_token(token=token):
        return RedirectResponse("/login", status_code=302)
            
    return FileResponse("static/html/profile.html")

@router.post("/API/profile")
async def post_get_profile_data(request: Request, username: UsernameForm = Body(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return RedirectResponse("/login", status_code=302)
    token_data = verify_token(token=token)
    if not token_data:
        return RedirectResponse("/login", status_code=302)
    profile_data = await get_profile_data_by_username(db=db, username=username.username)
    return profile_data