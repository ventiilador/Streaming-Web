from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import login, register, home, profile, video, default

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(login.router)
app.include_router(register.router)
app.include_router(home.router)
app.include_router(profile.router)
app.include_router(video.router)
app.include_router(default.router)