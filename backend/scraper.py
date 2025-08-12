from bs4 import BeautifulSoup
import requests
import re
import time
import os

print("Put some skills you are familiar with (comma separated, e.g., python, django, javascript):")
familiar_skills_input = input('>')

familiar_skills = [skill.strip().lower() for skill in familiar_skills_input.split(',')]
print(f"Filtering out jobs requiring any of these skills: {familiar_skills}")

def get_job_id_from_url(url):
    match = re.search(r'jobid-([^&]+)', url)
    return match.group(1) if match else None

def finding_jobs():
    html_text = requests.get('https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python&txtLocation=').text
    soup = BeautifulSoup(html_text, 'lxml')

    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
    for idx, job in enumerate(jobs):
        published_date_tag = job.find('span', class_='sim-posted')
        published_date = published_date_tag.span.text.strip() if published_date_tag and published_date_tag.span else 'N/A'

        if any(x in published_date.lower() for x in ["few", "hour", "day", "just now"]):
            
            
            company_name_tag = job.find('h3', class_='joblist-comp-name')
            company_name = company_name_tag.text.strip() if company_name_tag else 'N/A'

            h2_tag = job.find('h2', class_='heading-trun')
            if h2_tag:
                a_tag = h2_tag.find('a')
                job_title = a_tag.get_text(strip=True) if a_tag else 'N/A'
                job_link = a_tag['href'] if a_tag else 'N/A'
            else:
                job_title = 'N/A'
                job_link = 'N/A'

            skills_tag = job.find('span', class_='srp-skills')
            if skills_tag:
                skills = skills_tag.text.strip()
            else:
                a_tag_skills = job.find('a', class_='posoverlay_srp')
                if a_tag_skills and a_tag_skills.has_attr('onclick'):
                    onclick_text = a_tag_skills['onclick']
                    pattern = r"logViewUSBT\([^']*'[^']*','[^']*','([^']*)'"
                    match = re.search(pattern, onclick_text)
                    if match:
                        skills_str = match.group(1)
                        skills = ', '.join([s.strip() for s in skills_str.split(',')])
                    else:
                        skills = 'N/A'
                else:
                    skills = 'N/A'

            job_skills = [skill.strip().lower() for skill in skills.split(',')]

            
            location = 'N/A'
            experience = 'N/A'

            details_ul = job.find('ul', class_='top-jd-dtl mt-16 clearfix')
            if details_ul:
                location_li = details_ul.find('li', class_='srp-zindex location-tru')
                if location_li:
                    location = location_li.get_text(strip=True)
                
                from bs4 import Tag

                experience_li = details_ul.find(
                    lambda tag: isinstance(tag, Tag) and
                        tag.name == 'li' and
                        tag.find('i', class_='srp-icons experience') is not None
                )
                if experience_li:
                    experience = experience_li.get_text(strip=True)
                else:
                    experience = 'N/A'

           
            if any(skill in job_skills for skill in familiar_skills):
                job_id = get_job_id_from_url(job_link) or f"job_{idx}"
                os.makedirs('backend/job_posts', exist_ok=True)
                filepath = f"backend/job_posts/{job_id}.txt"
                if not os.path.exists(filepath):
                    with open(filepath, "w", encoding='utf-8') as f:
                        f.write(f"Company Name : {company_name}\n")
                        f.write(f"Job Title : {job_title}\n")
                        f.write(f"Location : {location}\n")
                        f.write(f"Experience Required : {experience}\n")
                        f.write(f"Skills Required : {skills}\n")
                        f.write(f"Posted Date : {published_date}\n")
                        f.write(f"Job Link : {job_link}\n")
                    print(f"Saved: {filepath}")
                else:
                    print(f"Already saved: {filepath}")

if __name__ == '__main__':
    while True:
        finding_jobs()
        wait_minutes = 10
        print(f"Waiting for {wait_minutes} minutes...\n")
        time.sleep(60 * wait_minutes)