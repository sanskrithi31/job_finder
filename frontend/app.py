import streamlit as st
from bs4 import BeautifulSoup
import requests
import re
from groq import Groq


GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
MODEL_NAME = "llama-3.3-70b-versatile"


st.title("TimesJobs Scraper + AI Outreach Mail Generator")

keywords_input = st.text_input("Enter keywords (comma separated)", "python,django,javascript")
locations_input = st.text_input("Enter locations (comma separated)", "hyderabad,bangalore")
skills_input = st.text_input("Enter your familiar skills to filter jobs", "python,django")


def get_job_id_from_url(url):
    match = re.search(r'jobid-([^&]+)', url)
    return match.group(1) if match else None

def scrape_jobs_for_keyword_location(keyword, location, familiar_skills):
    url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={keyword}&txtLocation={location}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    html_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_text, 'lxml')

    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
    results = []
    for job in jobs:
        published_date_tag = job.find('span', class_='sim-posted')
        published_date = published_date_tag.span.text.strip() if published_date_tag and published_date_tag.span else 'N/A'

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

        if not any(skill in job_skills for skill in familiar_skills):
            continue

        location_text = 'N/A'
        experience_text = 'N/A'
        details_ul = job.find('ul', class_='top-jd-dtl mt-16 clearfix')
        if details_ul:
            location_li = details_ul.find('li', class_='srp-zindex location-tru')
            if location_li:
                location_text = location_li.get_text(strip=True)

            from bs4 import Tag
            experience_li = details_ul.find(
                lambda tag: isinstance(tag, Tag) and
                            tag.name == 'li' and
                            tag.find('i', class_='srp-icons experience') is not None
            )
            if experience_li:
                experience_text = experience_li.get_text(strip=True)

        job_id = get_job_id_from_url(job_link) or job_title[:10].replace(" ", "_")
        results.append({
            "company_name": company_name,
            "job_title": job_title,
            "location": location_text,
            "experience": experience_text,
            "skills": skills,
            "posted_date": published_date,
            "job_link": job_link,
            "job_id": job_id
        })
    return results


def generate_outreach_email(job):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""
    Write a professional but friendly job outreach email to {job['company_name']} 
    for the position '{job['job_title']}' in {job['location']}.
    Mention my skills ({job['skills']}) and how I match their requirements.
    Keep it short (150 words max) and persuasive.
    """
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content


if st.button("Start Scraping & Generate Emails"):
    keywords = [k.strip().lower() for k in keywords_input.split(',')]
    locations = [l.strip().lower() for l in locations_input.split(',')]
    familiar_skills = [s.strip().lower() for s in skills_input.split(',')]

    all_jobs = []
    for keyword in keywords:
        for location in locations:
            st.write(f"Searching for '{keyword}' jobs in '{location}'...")
            jobs = scrape_jobs_for_keyword_location(keyword, location, familiar_skills)
            all_jobs.extend(jobs)

    if not all_jobs:
        st.warning("No matching jobs found.")
    else:
        st.success(f"Found {len(all_jobs)} matching jobs!")
        for job in all_jobs:
            st.markdown(f"### [{job['job_title']}]({job['job_link']})")
            st.write(f"**Company:** {job['company_name']}")
            st.write(f"**Location:** {job['location']}")
            st.write(f"**Experience:** {job['experience']}")
            st.write(f"**Skills Required:** {job['skills']}")
            st.write(f"**Posted:** {job['posted_date']}")
            
            
            with st.spinner("✍ Generating outreach email..."):
                email_text = generate_outreach_email(job)
            st.markdown("**Outreach Email:**")
            st.write(email_text)
            st.write("---")
