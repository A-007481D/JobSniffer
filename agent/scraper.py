import requests
from bs4 import BeautifulSoup

def fetch_jobs():
    url = "https://ma.indeed.com/"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    for card in soup.select(".job-card"):
        title = card.select_one(".title").get_text(strip=True)
        link  = card.select_one("a")["href"]
        jobs.append({"title": title, "link": link})
    return jobs
