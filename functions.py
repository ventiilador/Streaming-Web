from fastapi import Cookie, Request, UploadFile
from typing import Optional
from fastapi.responses import RedirectResponse
from auth import verify_token
from datetime import datetime, timedelta

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


def pretty_date(date) -> str:
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date)
        except ValueError:
            return "invalid date"

    now = datetime.now()
    delta = now - date

    if delta.total_seconds() < 0:
        return date.strftime("on %B %d, %Y at %H:%M")

    seconds = int(delta.total_seconds())

    if seconds < 10:
        return "just now"
    elif seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''} ago"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 172800:
        return "yesterday"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = seconds // 604800
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        return date.strftime("on %B %d, %Y at %H:%M")