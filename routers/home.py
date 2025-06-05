from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, FileResponse
from auth import verify_token
from crud import get_user_data_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter()

@router.get("/home")
def get_home(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        return RedirectResponse("/login", status_code=302)
    if not verify_token(token=token):
        return RedirectResponse("/login", status_code=302)
            
    return FileResponse("static/html/home.html")

@router.get("/API/home")
async def get_home_data(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return RedirectResponse("/login", status_code=302)
    token_data = verify_token(token=token)
    if not token_data:
        return RedirectResponse("/login", status_code=302)
    
    user_data = await get_user_data_by_id(db=db, id=token_data["user_id"])
    if user_data:
        return user_data
    return {"error":"err"}
