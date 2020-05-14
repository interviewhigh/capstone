# Authors: Interview High - Mike Menendez, Interivew High - Jesus Bernal Lopez
# Date: May 12, 2020
# Description: This is the main driver web server. This backend serves all endpoints
#              and renders the requested web pages on the fly via Jinja2 templates.

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiohttp
from constants import data, archive

# Initialize application
app = FastAPI()
# Mount templates directory for Jinja rendering
templates = Jinja2Templates(directory="templates")
# Mount static directory as the root
app.mount("/static", StaticFiles(directory="static"), name="static")

# Website content
PRESENTATION_TEAMS = data
ARCHIVE = archive

@app.on_event("startup")
async def startup_event():
    PRESENTATION_TEAMS.sort(key=lambda k: k['zoom_number'])
    for team in PRESENTATION_TEAMS:
        for student in team['team']['members']:
            student['links'].sort(key=lambda k: k[0])
    PRESENTATION_TEAMS.insert(0, PRESENTATION_TEAMS[9])
    PRESENTATION_TEAMS.pop(10)


# Index entrypoint for website.
@app.get("/", status_code=200)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "projects": PRESENTATION_TEAMS,
        "page": "home"
    })


# Health check for SSL terminating proxy
@app.get("/health", status_code=200)
async def health_check(request: Request):
    return ""


# Render student capstone page 
@app.get("/project/{project_id}", status_code=200)
async def project(request: Request, project_id: str = None):
    team = next(team for team in PRESENTATION_TEAMS if team['id'] == project_id)
    return templates.TemplateResponse("project.html",
                                      {"request": request, "team": team})


@app.get("/about", status_code=200)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {
        "request": request,
        "page": "about"
    })


@app.get("/presentations", status_code=200)
async def presentations(request: Request):
    return templates.TemplateResponse("presentations.html", {
        "request": request,
        "page": "presentations"
    })


@app.get("/contact", status_code=200)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "page": "contact"
    })


@app.get("/archive", status_code=200)
async def archive(request: Request):
    return templates.TemplateResponse("archive.html", {
        "request": request,
        "archive": ARCHIVE,
        "page": "archive",
    })


# 404 error handling
@app.get("/.*", status_code=404)
async def err_render(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})
