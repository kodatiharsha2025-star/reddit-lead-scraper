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

# Using Nitter/RSS alternative feed endpoint for Reddit
url = "https://www.reddit.com/r/forhire+videoediting/new.json?limit=25"
headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"}

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    posts = response.json().get("data", {}).get("children", [])
    existing_urls = sheet.col_values(4)
    
    count = 0
    for item in posts:
        post = item.get("data", {})
        title = post.get("title", "")
        permalink = post.get("permalink", "")
        post_url = f"https://reddit.com{permalink}"
        
        if post_url and post_url not in existing_urls:
            created_utc = post.get("created_utc", 0)
            post_time = datetime.utcfromtimestamp(created_utc).strftime('%Y-%m-%d %H:%M') if created_utc else "N/A"
            author = str(post.get("author", "[deleted]"))
            
            sheet.append_row([
                post_time,
                author,
                title,
                post_url,
                "New Lead"
            ])
            count += 1
            
    print(f"Successfully added {count} rows to Google Sheets.")
else:
    print(f"Failed response text: {response.text}")
