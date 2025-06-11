from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, FileResponse
from crud import get_user_data_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from functions import require_authenticated_user

router = APIRouter()

@router.get("/home")
def get_home(redirect=Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    return FileResponse(
        "static/html/home.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@router.get("/API/home")
async def get_home_data(db: AsyncSession = Depends(get_db), data=Depends(require_authenticated_user())):
    
    if isinstance(data, RedirectResponse):
        return data
    
    user_data = await get_user_data_by_id(db=db, id=data["user_id"])
    if user_data:
        return user_data
    return {"error":"Error getting data"}