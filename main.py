# Authors: Interview High - Mike Menendez, Interivew High - Jesus Bernal Lopez
# Date: May 12, 2020
# Description: This is the main driver web server. This backend serves all endpoints
#              and renders the requested web pages on the fly via Jinja2 templates.

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiohttp
import requests
from bs4 import BeautifulSoup as bs

# Initialize application
app = FastAPI()
# Mount templates directory for Jinja rendering
templates = Jinja2Templates(directory="templates")
# Mount static directory as the root
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables to fill at launch
PRESENTATION_TEAMS = dict()
BASE_URL = 'https://itcdland.csumb.edu/scdcapstone/'

@app.on_event("startup")
async def startup_event():
    await fetch_home_page()    
    await get_team_info()
    return

# Index entrypoint for website.
@app.get("/", status_code=200)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "projects": PRESENTATION_TEAMS})

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

@app.get("/presentations", status_code=200)
async def presentations(request: Request):
    return templates.TemplateResponse("presentations.html", {"request": request})

@app.get("/contact", status_code=200)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

# 404 error handling
@app.get("/.*", status_code=404)
async def err_render(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})

async def fetch_home_page():
    website = requests.get(BASE_URL + "index1.php", verify=False).text
    html = bs(website, 'html.parser')
    spans = html.find_all('span', {'class': 'capstonesPhp'})
    for span in spans:
        info = span.find('a')
        key = info['href']
        image = info.find('img')['src']
        team_name = info.find('strong').text

        PRESENTATION_TEAMS[key] = {
            'id': str(key).split('=')[-1],
            'image': image,
            'team': {
                'name': team_name
            }
        }

async def get_team_info():
    for key in PRESENTATION_TEAMS:
        website = requests.get(BASE_URL + key, verify=False).text
        html = bs(website, 'html.parser')

        students = html.find_all('span', {'class': 'students'})
        PRESENTATION_TEAMS[key]['team']['members'] = list()
        for student in students:
            info  = student.find('span', {'class': 'capstonestudentinfo'})
            name = student.find('strong').text
            image = info.find('img')['src']
            major = student.find('i').text