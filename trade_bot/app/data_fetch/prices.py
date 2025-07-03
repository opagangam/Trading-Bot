import yfinance as yf
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from broker_api.finnhub_api import get_stock_quote
import pandas as pd
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def calculate_price_change(current: float, previous: float) -> dict:
    try:
        if not previous or previous == 0:
            return {"abs_change": 0.0, "percent_change": 0.0}
        abs_change = round(current - previous, 2)
        percent_change = round((abs_change / previous) * 100, 2)
        return {"abs_change": abs_change, "percent_change": percent_change}
    except Exception as e:
        logger.error(f"Price change calculation error: {e}")
        return {"abs_change": 0.0, "percent_change": 0.0}

def format_timestamp(ts, is_indian=False) -> str:
    try:
        if isinstance(ts, pd.Timestamp):
            ts = ts.to_pydatetime()
        tz = pytz.timezone("Asia/Kolkata") if is_indian else pytz.timezone("US/Eastern")
        return ts.astimezone(tz).isoformat()
    except Exception as e:
        logger.warning(f"Timestamp formatting error: {e}")
        return str(ts)

def is_market_open(market: str) -> bool:
    now = datetime.now(pytz.timezone("Asia/Kolkata" if market == "IN" else "US/Eastern"))
    weekday = now.weekday()
    current_time = now.time()

    if weekday >= 5:  # Weekend
        return False

    if market == "IN":
        # NSE/BSE hours: 9:15 AM to 3:30 PM IST
        return current_time >= datetime.strptime("09:15", "%H:%M").time() and current_time <= datetime.strptime("15:30", "%H:%M").time()

    elif market == "US":
        # NASDAQ hours: 9:30 AM to 4:00 PM ET
        return current_time >= datetime.strptime("09:30", "%H:%M").time() and current_time <= datetime.strptime("16:00", "%H:%M").time()

    return False  # Default fallback

def get_price(ticker: str, period="4d", interval="5m") -> dict:
    is_indian = ticker.endswith(".NS") or ticker.endswith(".BO")
    market = "IN" if is_indian else "US"
    market_open = is_market_open(market)

    try:
        if is_indian:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                threads=True,
                auto_adjust=False
            )
            if isinstance(df.columns,pd.MultiIndex):
                df.columns=df.columns.get_level_values(0)

            if df.empty:
                return {
                    "error": f"No price data found for {ticker}. DataFrame is empty.",
                    "source": "yfinance",
                    "success": False,
                    "market_open": market_open
                }

            if "Close" not in df.columns:
                logger.warning(f"'Close' column not found. Available columns: {df.columns.tolist()}")
                return {
                    "error": f"'Close' column missing for {ticker}. Available columns: {df.columns.tolist()}",
                    "source": "yfinance",
                    "success": False,
                    "market_open": market_open
                }

            try:
                df = df.dropna(subset=["Close"])
            except KeyError as e:
                logger.error(f"KeyError dropping NaNs: {e}, available columns: {df.columns.tolist()}")
                return {
                    "error": f"KeyError dropping NaNs in 'Close'. Columns: {df.columns.tolist()}",
                    "source": "yfinance",
                    "success": False,
                    "market_open": market_open
                }

            if df.empty:
                return {
                    "error": f"No usable rows in price data for {ticker} after dropping NaNs.",
                    "source": "yfinance",
                    "success": False,
                    "market_open": market_open
                }

            current_close = float(df.iloc[-1]["Close"])
            prev_close = float(df.iloc[-2]["Close"]) if len(df) > 1 else current_close
            timestamp = format_timestamp(df.index[-1], is_indian=True)
            change = calculate_price_change(current_close, prev_close)

            return {
                "ticker": ticker,
                "source": "yfinance",
                "success": True,
                "market_open": market_open,
                "timestamp": timestamp,
                "current": current_close,
                "previous_close": prev_close,
                "price_change": change["abs_change"],
                "percent_change": change["percent_change"],
                "note": "Market is closed. Returning last known price." if not market_open else "Live data."
            }


        # Fallback for US/global stocks
        result = get_stock_quote(ticker)

        if "error" in result:
            return {**result, "success": False, "market_open": market_open}

        result["success"] = True
        result["market_open"] = market_open
        result["note"] = "Market is closed. Returning last known price." if not market_open else "Live data."
        return result

    except Exception as e:
        logger.exception(f"Unhandled exception in get_price for {ticker}")
        return {
            "error": f"Unhandled exception fetching price for {ticker}: {str(e)}",
            "source": "yfinance" if is_indian else "finnhub",
            "success": False,
            "market_open": market_open
        }

