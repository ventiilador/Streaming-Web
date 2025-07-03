from fastapi import APIRouter, Body, Depends
from fastapi.responses import RedirectResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from functions import require_authenticated_user
from crud import get_contacts, mail_data, accept_followup, deny_followup
from schemas import AcceptFollower, DenyFollower

router = APIRouter()

@router.get("/mail")
def get_mail(redirect=Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    return FileResponse(
        "static/html/mail.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@router.get("/get_mail_data")
async def get_mail_data(data=Depends(require_authenticated_user()), db: AsyncSession=Depends(get_db)):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    
    return await mail_data(db=db, user_id=user_id)

@router.post("/accept_follow")
async def post_accept_follow(
    followup_data: AcceptFollower = Body(...),
    data=Depends(require_authenticated_user()),
    db: AsyncSession = Depends(get_db)):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    return await accept_followup(db=db, user_id=user_id,
                                followup_id=followup_data.id,
                                follower_id=followup_data.follower_id)

@router.post("/deny_follow")
async def post_deny_follow(
    followup_data: DenyFollower = Body(...),
    data=Depends(require_authenticated_user()),
    db: AsyncSession = Depends(get_db)):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]

    return await deny_followup(db=db, user_id=user_id, followup_id=followup_data.id)

@router.get("/get_chats")
async def get_chats(data=Depends(require_authenticated_user()), db: AsyncSession=Depends(get_db)):

    if isinstance(data, RedirectResponse):
        return data
    
    user_id = data["user_id"]
    
    return await get_contacts(db=db, user_id=user_id)