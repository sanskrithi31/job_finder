# JobScrape AI

An **AI-powered job scraping and outreach automation tool** built with **Python, Streamlit, and Groq API**.  
It scrapes job postings from **TimesJobs** based on user-defined keywords, locations, and skills, then generates **tailored outreach emails** using AI.

---

## 🚀 Features

- 🔍 **Job Search Automation** – Scrapes jobs by keywords, locations, and filters them by your skills.  
- 🧠 **AI Outreach Email Generator** – Uses **Groq LLaMA 3.3 model** to create personalized emails for each job.  
- 📑 **Detailed Job Info** – Extracts title, company name, location, required skills, experience, and posted date.  
- 🛡 **Anti-Bot Bypass** – Custom HTTP headers to mimic real browsers and avoid scraping blocks.  
- ⚡ **Streamlit UI** – Simple web-based interface for easy interaction.  

---

## 🛠 Tech Stack

- **Python** – Core programming language
- **Streamlit** – Web app UI
- **BeautifulSoup4** – HTML parsing
- **Requests** – HTTP requests for scraping
- **Groq API** – AI model integration
- **Regex** – Job ID and skill extraction

---

## 📂 Project Structure

job_finder/
│
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
├── .gitignore # Ignore sensitive files
├── README.md # Project documentation
└── .streamlit/
└── secrets.toml # Stores Groq API key (not pushed to GitHub)
