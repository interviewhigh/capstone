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
import pprint

# Initialize application
app = FastAPI()
# Mount templates directory for Jinja rendering
templates = Jinja2Templates(directory="templates")
# Mount static directory as the root
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global variables to fill at launch
PRESENTATION_TEAMS = list()
BASE_URL = 'https://itcdland.csumb.edu/scdcapstone/'

@app.on_event("startup")
async def startup_event():
    await fetch_home_page()    
    await get_team_info()
    return

# Index entrypoint for website.
@app.get("/", status_code=200)
async def index(request: Request):
    pprint.pprint(PRESENTATION_TEAMS[0])
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

async def fetch_home_page():
    website = requests.get(BASE_URL + "index1.php", verify=False).text
    html = bs(website, 'html.parser')
    spans = html.find_all('span', {'class': 'capstonesPhp'})
    for span in spans:
        info = span.find('a')
        key = info['href']
        image = info.find('img')['src']
        team_name = info.find('strong').text

        PRESENTATION_TEAMS.append({
            'id': str(key).split('=')[-1],
            'image': image,
            'team': {
                'name': team_name
            }
        })

async def get_team_info():
    for i, team in enumerate(PRESENTATION_TEAMS):
        website = requests.get(BASE_URL + 'project1.php?project_id=' + team['id'], verify=False).text
        html = bs(website, 'html.parser')

        description = html.find('div', {'class': 'col-md-8'}).text.split('Presentation Room:')[-1].strip()
        team['team']['description'] = description

        students = html.find_all('span', {'class': 'students'})
        team['team']['members'] = list()

        for student in students:
            parse_student_info(i, student)

def parse_student_info(index, student):
    """
    @param key
        - The key to index for the PRESENTATION_TEAMS
    @param student
        - The student span html
    
    It parses the student information and adds it to the PRESENTATION_TEAMS
    based on the key(their team) based in
    """
    info  = student.find('span', {'class': 'capstonestudentinfo'})
    name = student.find('strong').text
    image = info.find('img')['src']
    major = student.find('i').text
    email = parse_student_email(student.text)
    resume, github, linkedin = get_resume_linkedin_github(student.find_all('a'))
    PRESENTATION_TEAMS[index]['team']['members'].append({
        'name': name,
        'image': image,
        'major': major,
        'email': email,
        'links': [
            ('Resume', resume),
            ('GitHub', github),
            ('LinkedIn', linkedin)
        ],
    })


def parse_student_email(text):
    """
    @param text
        - raw text in the html
    @return 
        - Users email
    """
    return [entry for entry in text.split(' ') if '@' in entry][0].split('CS')[-1]


def get_resume_linkedin_github(tags):
    """
    @param tags
        - All the a tags of the span
    @returns
        - The resume, linkedin and github profile link of the student
    """
    resume = ''
    linkedin = ''
    github = ''
    for tag in tags:
        if 'Resume' in tag.text:
            resume = tag['href']
        elif 'LinkedIn' in tag.text:
            linkedin = tag['href']
        elif 'GitHub' in tag.text:
            github = tag['href']
    return resume, github, linkedin
