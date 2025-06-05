from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, FileResponse
from auth import verify_token, create_access_token
from schemas import LoginForm
from crud import login
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

router = APIRouter()

@router.get("/login")
def get_login(request: Request):
    token = request.cookies.get("session_token")
    if token:
        if verify_token(token=token):
            return RedirectResponse("/home", status_code=302)
    return FileResponse("static/html/login.html")

@router.post("/login")
async def post_login(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if token:
        if verify_token(token=token):
            return RedirectResponse("/home", status_code=302)
    
    try:
        form = LoginForm(username=username, password=password)
    except ValueError as e:
        print(e)
        return RedirectResponse("/login?error=1", status_code=302)
    
    user = await login(db=db, username=form.username, password=form.password)

    if user:
        token = create_access_token(user_id=user.id)
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
    return RedirectResponse("/login?error=2", status_code=302)