import os
import json
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_json = os.environ.get("GCP_SA_KEY")
creds_dict = json.loads(creds_json)
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

gc = gspread.authorize(creds)
sheet = gc.open("Reddit Video Editor Leads").sheet1

subreddits = "forhire+videoediting+freelance_forhire"
url = f"https://www.reddit.com/r/{subreddits}/new.json?limit=15"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    posts = response.json()["data"]["children"]
    
    for item in posts:
        post = item["data"]
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        title_body = (title + " " + selftext).lower()
        
        if "video editor" in title_body or "hiring" in title_body:
            budget_keywords = ["$", "usd", "budget", "per hour", "month", "k/", "hr"]
            has_budget = any(keyword in title_body for keyword in budget_keywords)
            priority = "🔥 Hot Lead" if has_budget else ""
            
            post_time = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M')
            post_url = f"https://reddit.com{post.permalink}"
            author = str(post.get("author", "[deleted]"))
            
            existing_urls = sheet.col_values(4)
            if post_url not in existing_urls:
                sheet.append_row([
                    post_time,
                    author,
                    title,
                    post_url,
                    priority
                ])
