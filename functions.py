from fastapi import Cookie, Request, UploadFile
from typing import Optional
from fastapi.responses import RedirectResponse
from auth import verify_token

def require_authenticated_user():
    def dependency(
        request: Request,
        session_token: Optional[str] = Cookie(None)
    ):
        if not session_token:
            return RedirectResponse(url="/login", status_code=302)
        
        token_data = verify_token(session_token)
        if not token_data:
            return RedirectResponse(url="/login", status_code=302)
        
        return {"user_id": token_data["user_id"]}
    return dependency


def redirect_if_authenticated(redirect_to="/home"):
    def dependency(
        request: Request,
        session_token: Optional[str] = Cookie(None)
    ):
        if not session_token:
            return None
        
        token_data = verify_token(session_token)
        if token_data:
            return RedirectResponse(url=redirect_to, status_code=302)
        
        return None
    return dependency

async def save_upload_file(upload_file: UploadFile, destination_path: str):
    with open(destination_path, "wb") as out_file:
        content = await upload_file.read()
        out_file.write(content)