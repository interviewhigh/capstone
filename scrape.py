import requests
from bs4 import BeautifulSoup as bs


PRESENTATION_TEAMS = list()
BASE_URL = 'https://itcdland.csumb.edu/scdcapstone/'

# Scrape data from website
async def fetch_home_page():
    """
    Gets the basic project information to use by others to fill rest of fields
    """
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
    @param index
        - The index of the team on the teams global variable
    @param key
        - The key to index for the PRESENTATION_TEAMS
    @param student
        - The student span html
    
    It parses the student information and adds it to the PRESENTATION_TEAMS
    based on the key(their team) based in
    """
    info  = student.find('span', {'class': 'capstonestudentinfo'})
    name = student.find('strong').text.strip()
    image = info.find('img')['src']
    major = student.find('i').text
    email = parse_student_email(student.text)

    PRESENTATION_TEAMS[index]['team']['members'].append({
        'name': name,
        'image': image,
        'major': major,
        'email': email,
        'links': list(),
    })
    get_resume_linkedin_github(index, student.find_all('a'))


def parse_student_email(text):
    """
    @param text
        - raw text in the html
    @return 
        - Users email
    """
    return [entry for entry in text.split(' ') if '@' in entry][0].split('CS')[-1]


def get_resume_linkedin_github(index, tags):
    """
    @param index
        - The index of the team on the teams global variable
    @param tags
        - All the a tags of the span
    """

    length = len(PRESENTATION_TEAMS[index]['team']['members']) - 1
    for tag in tags:
        if 'Resume' in tag.text:
            PRESENTATION_TEAMS[index]['team']['members'][length]['links'].append(('Resume', tag['href']))
        elif 'LinkedIn' in tag.text:
            PRESENTATION_TEAMS[index]['team']['members'][length]['links'].append(('LinkedIn', tag['href']))
        elif 'GitHub' in tag.text:
            PRESENTATION_TEAMS[index]['team']['members'][length]['links'].append(('GitHub', tag['href']))
