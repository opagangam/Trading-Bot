import finnhub
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Setup Finnhub client
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

def get_stock_quote(ticker: str):
    try:
        quote = finnhub_client.quote(ticker)
        return {
            "current": quote["c"],
            "high": quote["h"],
            "low": quote["l"],
            "open": quote["o"],
            "previous_close": quote["pc"]
        }
    except Exception as e:
        return {"error": str(e)}

def get_company_news(ticker: str):
    try:
        # Step 1: Resolve correct symbol
        res = finnhub_client.symbol_lookup(ticker)
        if not res or 'result' not in res or not res['result']:
            return [{"headline": f"Symbol lookup failed for {ticker}"}]

        # Prefer exact match if available
        exact_match = next((item for item in res['result'] if item['symbol'].upper() == ticker.upper()), res['result'][0])
        resolved_symbol = exact_match['symbol']
        company_name = exact_match.get('description', '').split(' ')[0]  # e.g., "Apple Inc" → "Apple"

        # Step 2: Fetch news
        today = datetime.now().strftime('%Y-%m-%d')
        past = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        news = finnhub_client.company_news(resolved_symbol, _from=past, to=today)

        if not isinstance(news, list):
            return [{"headline": "No news found."}]

        # Step 3: Filter for relevance (headline/company name)
        filtered_news = [
            article for article in news
            if ticker.upper() in article.get('headline', '').upper()
            or company_name.upper() in article.get('headline', '').upper()
        ]

        # Step 4: Fallback to general list if too few
        final_news = filtered_news if len(filtered_news) >= 3 else news

        # Step 5: Format and return
        return [{
            "headline": article.get("headline", ""),
            "summary": article.get("summary", ""),
            "source": article.get("source", ""),
            "url": article.get("url", ""),
            "datetime": datetime.fromtimestamp(article.get("datetime", 0)).strftime('%Y-%m-%d %H:%M:%S')
        } for article in final_news[:5]]

    except Exception as e:
        return [{"headline": f"Error fetching news: {str(e)}"}]

