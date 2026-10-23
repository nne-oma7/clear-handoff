from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth import require_staff
from database import Base, engine
import models
from routes import router


BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ClearHandoff API",
    description="A complaint management and engineering handoff platform.",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)

app.include_router(router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/track")
def track_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context={}
    )


@app.get("/dashboard", dependencies=[Depends(require_staff)])
def support_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={}
    )