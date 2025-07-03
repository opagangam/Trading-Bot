import datetime
import yfinance as yf
from broker_api.finnhub_api import get_company_news
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

# Optional: SerpAPI or News API key for Indian stock news
import os
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def fetch_news_google_news(ticker: str, max_articles=5):
    """Fetch latest news using Google News RSS"""
    search_term = ticker.replace(".NS", "").replace(".BO", "")
    url = f"https://news.google.com/rss/search?q={search_term}+stock+india"

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.findAll("item")[:max_articles]
        return [{
            "title": item.title.text,
            "link": item.link.text,
            "source": item.source.text if item.source else "Google News",
            "pubDate": item.pubDate.text
        } for item in items]
    except Exception as e:
        return [{"title": f"Error fetching Google News RSS: {str(e)}"}]


def fetch_news_serpapi(ticker: str, max_articles=5):
    """Use SerpAPI for richer structured news (if available)"""
    if not SERPAPI_KEY:
        print("[DEBUG] SERPAPI_KEY not set. Skipping SerpAPI.")
        return []
    print(f"[DEBUG] Calling SerpAPI for: {ticker}")

    query = ticker.replace(".NS", "") + " stock news"
    try:
        url = f"https://serpapi.com/search.json?q={query}&tbm=nws&api_key={SERPAPI_KEY}"
        response = requests.get(url, timeout=10).json()
        return [{
            "title": item["title"],
            "link": item["link"],
            "source": item.get("source", "SerpAPI"),
            "pubDate": item.get("date", "")
        } for item in response.get("news_results", [])[:max_articles]]
    except Exception as e:
        return [{"title": f"Error fetching SerpAPI news: {str(e)}"}]


def get_news(ticker: str, max_articles=5):
    """Universal news fetcher for both Indian and Global stocks"""
    is_indian = ticker.endswith(".NS") or ticker.endswith(".BO")

    if is_indian:
        stock = yf.Ticker(ticker)
        try:
            # Try yfinance business summary
            info = stock.info
            summary = info.get("longBusinessSummary", "")

            # --- FETCH GOOGLE NEWS ---
            google_news = fetch_news_google_news(ticker, max_articles)

            if google_news and isinstance(google_news, list) and "Error" not in google_news[0].get("title", ""):
                print(f"[DEBUG] Returning {len(google_news)} articles from Google News.")
                return google_news

            # --- FALLBACK: TRY SERPAPI ---
            serp_news = fetch_news_serpapi(ticker, max_articles)
            if serp_news and isinstance(serp_news, list) and serp_news[0].get("title"):
                print(f"[DEBUG] Returning {len(serp_news)} articles from SerpAPI.")
                return serp_news

            # Fallback to business summary if no valid news found
            return [{
                "title": summary or "No recent news found.",
                "source": "Yahoo Finance"
            }]

        except Exception as e:
            return [{"title": f"Error fetching Indian stock news: {str(e)}"}]

    else:
        # International stocks via Finnhub
        try:
            news_items = get_company_news(ticker)

            # ✅ Defensive check: ensure we got a list
            if not isinstance(news_items, list):
                return [{
                    "title": f"Error: Unexpected response format from Finnhub: {news_items}"
                }]

            return [{
                "title": item.get("headline"),
                "summary": item.get("summary", ""),
                "source": item.get("source"),
                "link": item.get("url"),
                "pubDate": item.get("datetime")
            } for item in news_items[:max_articles]]

        except Exception as e:
            return [{"title": f"Error fetching international news: {str(e)}"}]

