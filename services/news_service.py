import feedparser
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_news_from_rss(feed_url, limit=3):
    """Generic function to fetch news from RSS."""
    try:
        feed = feedparser.parse(feed_url)
        return [
            {"title": entry.title, "link": entry.link, "source": feed.feed.title if hasattr(feed.feed, 'title') else "RSS"}
            for entry in feed.entries[:limit]
        ]
    except Exception as e:
        return {"error": str(e)}

def get_tech_news_es(limit=3):
    """Fetch tech news from Xataka (Spanish)."""
    return get_news_from_rss("https://feeds.feedburner.com/xataka2", limit)

def get_economic_news_es(limit=3):
    """Fetch economic news from Expansión (Spanish)."""
    return get_news_from_rss("https://www.expansion.com/rss/portada.xml", limit)
