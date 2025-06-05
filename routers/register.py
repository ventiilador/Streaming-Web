from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, FileResponse
from auth import verify_token, create_access_token
from schemas import RegisterForm
from crud import register
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter()

@router.get("/register")
def get_register(request: Request):
    token = request.cookies.get("session_token")
    if token:
        if verify_token(token=token):
            return RedirectResponse("/home", status_code=302)
    return FileResponse("static/html/register.html")

@router.post("/register")
async def register_login(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if token:
        if verify_token(token=token):
            return RedirectResponse("/home", status_code=302)
    
    try:
        form = RegisterForm(username=username, email=email, password=password)
    except ValueError as e:
        print(e)
        return RedirectResponse("/register?error=1", status_code=302)
    
    newuser = await register(db=db, username=form.username, email=email, password=form.password)

    if newuser:
        token = create_access_token(user_id=newuser.id)
        response = RedirectResponse("/home", status_code=302, headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        })
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            samesite="lax"
        )
        return response
    return RedirectResponse("/register?error=2", status_code=302)