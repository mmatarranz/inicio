import feedparser
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_tech_news(limit=3):
    """Fetch top tech news using RSS (fallback to NewsAPI if key provided)."""
    news_api_key = os.getenv("NEWS_API_KEY")
    
    if news_api_key:
        url = f"https://newsapi.org/v2/top-headlines?category=technology&language=en&pageSize={limit}&apiKey={news_api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            return [
                {"title": a["title"], "link": a["url"], "source": a["source"]["name"]}
                for a in articles
            ]
        except Exception:
            pass # Fallback to RSS if API fails
            
    # RSS Fallback (BBC Tech or similar)
    feed_url = "https://feeds.bbci.co.uk/news/technology/rss.xml"
    try:
        feed = feedparser.parse(feed_url)
        return [
            {"title": entry.title, "link": entry.link, "source": "BBC"}
            for entry in feed.entries[:limit]
        ]
    except Exception as e:
        return {"error": str(e)}
