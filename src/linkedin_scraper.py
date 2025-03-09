import requests
import json
import time
import os

API_KEY = "67b20d41b4930148aaae115b"
BASE_URL = "https://api.scrapingdog.com/linkedinjobs/"
LAST_PAGE_FILE = "last_page.json"
JOBS_FILE = "../data/linkedin_jobs.json"

def load_last_page():
    if os.path.exists(LAST_PAGE_FILE):
        try:
            with open(LAST_PAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("last_page", 1)
        except json.JSONDecodeError:
            pass
    return 1

def save_last_page(page):
    with open(LAST_PAGE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_page": page}, f, ensure_ascii=False, indent=4)

def job_exists(job_id):
    if not os.path.exists(JOBS_FILE):
        return False
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                job = json.loads(line.strip().rstrip(","))
                if job.get("job_id") == job_id:
                    return True
            except json.JSONDecodeError:
                continue
    return False

def append_job_to_file(job):
    mode = "a" if os.path.exists(JOBS_FILE) else "w"
    with open(JOBS_FILE, mode, encoding="utf-8") as f:
        f.write(json.dumps(job, ensure_ascii=False) + ",\n")

def fetch_jobs(page):
    params = {"api_key": API_KEY, "field": " ", "geoid": "101620260", "page": str(page)}
    response = requests.get(BASE_URL, params=params)
    return response.json() if response.status_code == 200 else None

def fetch_job_details(job_id):
    url = f"https://api.scrapingdog.com/linkedinjobs?api_key={API_KEY}&job_id={job_id}"
    response = requests.get(url)
    return response.json()[0] if response.status_code == 200 else None

def scrape_linkedin_jobs():
    page = load_last_page()

    while True:
        print(f"📄 Fetching page {page}...")
        jobs_list = fetch_jobs(page)

        if not jobs_list:
            print("✅ No more jobs found, stopping.")
            break

        for job in jobs_list:
            job_id = job.get("job_id")
            if not job_id or job_exists(job_id):
                continue

            full_job_data = fetch_job_details(job_id)
            if not full_job_data:
                print(f"❌ Failed to fetch details for job {job_id}")
                continue

            merged_job = {**job, **{k: v for k, v in full_job_data.items() if k not in job and k not in ["similar_jobs", "people_also_viewed"]}}
            append_job_to_file(merged_job)
            print(f"✅ Added details for job {job_id}")
            time.sleep(1)

        save_last_page(page)
        page += 1

    print("🚀 Scraping completed.")

scrape_linkedin_jobs()