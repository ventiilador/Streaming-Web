from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, FileResponse
from functions import require_authenticated_user

router = APIRouter()

@router.get("/dashboard")
def get_dashboard(redirect = Depends(require_authenticated_user())):

    if isinstance(redirect, RedirectResponse):
        return redirect
    
    return FileResponse(
        "static/html/dashboard.html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
    })

