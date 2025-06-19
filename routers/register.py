from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse, FileResponse
from auth import create_access_token
from schemas import RegisterForm
from crud import register
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from functions import redirect_if_authenticated

router = APIRouter()

@router.get("/register")
def get_register(redirect=Depends(redirect_if_authenticated())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    return FileResponse("static/html/register.html")

@router.post("/register")
async def register_login(
    form: RegisterForm = Depends(RegisterForm.as_form),
    db: AsyncSession = Depends(get_db),
    redirect=Depends(redirect_if_authenticated())):
    
    if isinstance(redirect, RedirectResponse):
        return redirect
    
    newuser = await register(db=db, username=form.username, email=form.email, password=form.password)

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