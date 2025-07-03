import itertools
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, FileResponse
from auth import create_access_token
from schemas import LoginForm
from crud import login
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from functions import redirect_if_authenticated

router = APIRouter()

@router.get("/login")
def get_login(redirect=Depends(redirect_if_authenticated())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    return FileResponse("static/html/login.html")

@router.post("/login")
async def post_login(
    form: LoginForm = Depends(LoginForm.as_form),
    db: AsyncSession = Depends(get_db),
    redirect=Depends(redirect_if_authenticated())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    user = await login(db=db, username=form.username, password=form.password)

    if user:
        token = create_access_token(user_id=user.id)
        response = RedirectResponse("/home", status_code=302)
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            samesite="lax"
        )
        return response
    
    return RedirectResponse("/login?error=2", status_code=302)