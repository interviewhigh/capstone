# Authors: Interview High - Mike Menendez, Interivew High - Jesus Bernal Lopez
# Date: May 12, 2020
# Description: This is the main driver web server. This backend serves all endpoints
#              and renders the requested web pages on the fly via Jinja2 templates.

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiohttp

# Initialize application
app = FastAPI()
# Mount templates directory for Jinja rendering
templates = Jinja2Templates(directory="templates")
# Mount static directory as the root
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    return

# Index entrypoint for website.
@app.get("/", status_code=200)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Health check for SSL terminating proxy
@app.get("/health", status_code=200)
async def health_check(request: Request):
    return ""

# Render student capstone page 
@app.get("/project/{project_id}", status_code=200)
async def project(request: Request, project_id: str = None):
    return templates.TemplateResponse("project.html",
                                      {"request": request})

@app.get("/about", status_code=200)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", status_code=200)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# 404 error handling
@app.get("/.*", status_code=404)
async def err_render(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})
