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
url = f"https://www.reddit.com/r/{subreddits}/new.json?limit=25"

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

response = requests.get(url, headers=headers)
print(f"Reddit API Status: {response.status_code}")

if response.status_code == 200:
    posts = response.json()["data"]["children"]
    existing_urls = sheet.col_values(4)
    
    count = 0
    for item in posts:
        post = item["data"]
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        title_body = (title + " " + selftext).lower()
        
        post_url = f"https://reddit.com{post.permalink}"
        
        if post_url not in existing_urls:
            post_time = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M')
            author = str(post.get("author", "[deleted]"))
            
            budget_keywords = ["$", "usd", "budget", "per hour", "month", "k/", "hr", "pay"]
            has_budget = any(keyword in title_body for keyword in budget_keywords)
            priority = "🔥 Hot Lead" if has_budget else "Lead"
            
            sheet.append_row([
                post_time,
                author,
                title,
                post_url,
                priority
            ])
            count += 1

    print(f"Successfully added {count} new posts to sheet.")
