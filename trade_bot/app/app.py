from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from database.models import init_db, log_trade
from data_fetch.prices import get_price
from data_fetch.news import get_news
from sentiment.analyzer import analyze_news_sentiment
from trading_logic.strategy import trade_decision

init_db()

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Financial Trading Bot API"}

@app.get("/trade/{ticker}")
def auto_trade(ticker: str):
    # Use updated get_price (handles yfinance & finnhub)
    price_info = get_price(ticker)
    if "error" in price_info:
        return price_info

    # Use updated get_news (handles yfinance & finnhub)
    news = get_news(ticker)
    for article in news:
        print(f"Title: {article.get('title')}")
        print(f"Source: {article.get('source')}")
        print(f"PubDate: {article.get('pubDate')}")
        print("---")

    # Analyze sentiment
    sentiment = analyze_news_sentiment(news)

    # Safely calculate price change %
    current_price = price_info.get("current", 0)
    previous_close = price_info.get("previous_close", 0)

    if not previous_close or previous_close == 0:
        print(f"⚠️ Warning: previous_close is 0 or missing for {ticker}")
        price_change_pct = 0.0
    else:
        price_change_pct = ((current_price - previous_close) / previous_close) * 100

    # Make trade decision
    decision = trade_decision(sentiment, price_change_pct)

    # Log the trade
    log_trade(
        ticker=ticker,
        price=current_price,
        sentiment_score=sentiment,
        price_change_pct=price_change_pct,
        decision=decision
    )

    # Return response
    return {
        "ticker": ticker,
        "price": price_info,
        "sentiment": sentiment,
        "price_change_pct": round(price_change_pct, 2),
        "decision": decision
    }


import gradio as gr

def run_trade(ticker):
    response = auto_trade(ticker)
    output = f"""
📈 **Ticker**: {response['ticker']}
💵 **Price**: {response['price']['current']} (Previous: {response['price']['previous_close']})
📊 **Price Change %**: {round(response['price_change_pct'], 2)}%
🧠 **Sentiment Score**: {round(response['sentiment'], 2)}
🚦 **Decision**: {response['decision']}
"""
    return output

gradio_ui = gr.Interface(
    fn=run_trade,
    inputs=gr.Textbox(label="Enter Ticker Symbol (e.g., NFLX, RELIANCE.NS)"),
    outputs=gr.Markdown(label="Trading Decision"),
    title="📊 Auto-Trading Bot Interface",
    description="Enter a stock ticker to get price info, sentiment, and trading decision."
)

# Mount Gradio to FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gradio.routes import mount_gradio_app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app = mount_gradio_app(app, gradio_ui, path="/ui")

