from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import login, register, home, profile, video, default, media, dashboard, editVideo, settings, mail, chat, presence

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login.router)
app.include_router(register.router)
app.include_router(home.router)
app.include_router(profile.router)
app.include_router(video.router)
app.include_router(default.router)
app.include_router(media.router)
app.include_router(dashboard.router)
app.include_router(editVideo.router)
app.include_router(settings.router)
app.include_router(mail.router)
app.include_router(chat.router)
app.include_router(presence.router)