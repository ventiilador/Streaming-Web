import itertools
from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse, FileResponse
from crud import get_default_videos, get_user_data_by_id, get_user_preferences, get_videos_by_hashtag, search_channels, search_videos
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from functions import require_authenticated_user
from schemas import SearchForm

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

@router.post("/search")
async def post_search(
    form: SearchForm = Depends(SearchForm.as_form),
    data=Depends(require_authenticated_user()),
    db: AsyncSession = Depends(get_db)
    ):

    if isinstance(data, RedirectResponse):
        return data
    
    if form.type == "videos":
        videos = await search_videos(db, form.search, form.filter, form.offset)
        return {"videos": videos}
    else:
        channels = await search_channels(db, form.search, form.filter, form.offset)
        return {"channels": channels}
    
@router.get("/API/home_varied_search")
async def home_varied_search(
    offset: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    data=Depends(require_authenticated_user())
):
    user_id = data["user_id"]

    preferences = await get_user_preferences(db, user_id)
    
    if not preferences:
        videos = await get_default_videos(db, offset=offset, limit=limit)
        return {"videos": videos}

    hashtags = [p.hashtag_id for p in preferences]
    n_tags = len(hashtags)
    
    per_tag_limit = max(1, limit // n_tags)
    
    base_offset = offset // n_tags
    
    videos_per_tag = []
    for hashtag_id in hashtags:
        tag_videos = await get_videos_by_hashtag(db, hashtag_id, limit=per_tag_limit, offset=base_offset)
        videos_per_tag.append(tag_videos)

    varied_videos = []
    for group in itertools.zip_longest(*videos_per_tag):
        for video in group:
            if video:
                varied_videos.append(video)
    
    varied_videos = varied_videos[:limit]

    return {"videos": varied_videos}