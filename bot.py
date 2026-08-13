import os
import json
import feedparser
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

# Using RSS feed URL which is fully open and unblocked
rss_url = "https://www.reddit.com/r/forhire+videoediting/new.rss"
feed = feedparser.parse(rss_url)

existing_urls = sheet.col_values(4)
count = 0

for entry in feed.entries[:25]:
    title = entry.get("title", "")
    post_url = entry.get("link", "")
    post_time = entry.get("published", "").replace("T", " ")[:16]
    author = entry.get("author", "Reddit User")
    
    if post_url and post_url not in existing_urls:
        title_lower = title.lower()
        budget_keywords = ["$", "usd", "budget", "per hour", "month", "k/", "hr", "pay"]
        has_budget = any(keyword in title_lower for keyword in budget_keywords)
        priority = "🔥 Hot Lead" if has_budget else "New Lead"
        
        sheet.append_row([
            post_time,
            author,
            title,
            post_url,
            priority
        ])
        count += 1

print(f"Successfully added {count} leads via RSS feed.")
