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

url = "https://www.reddit.com/r/forhire/new.json?limit=25"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    posts = data["data"]["children"]
    existing_urls = sheet.col_values(4)
    
    count = 0
    for item in posts:
        post = item["data"]
        title = post.get("title", "")
        post_url = f"https://reddit.com{post.permalink}"
        
        if post_url not in existing_urls:
            post_time = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M')
            author = str(post.get("author", "[deleted]"))
            
            sheet.append_row([
                post_time,
                author,
                title,
                post_url,
                "New Lead"
            ])
            count += 1
            
    print(f"Added {count} posts.")
else:
    print(f"Failed to fetch: {response.text}")
