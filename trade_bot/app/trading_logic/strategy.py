def trade_decision(sentiment_score: float, price_change_pct: float) -> str:

    # Define tiers for sentiment
    strong_positive_sentiment = sentiment_score >= 0.5
    mild_positive_sentiment = 0.2 <= sentiment_score < 0.5
    neutral_sentiment = -0.2 < sentiment_score < 0.2
    mild_negative_sentiment = -0.5 < sentiment_score <= -0.2
    strong_negative_sentiment = sentiment_score <= -0.5

    # Define tiers for price momentum
    strong_upward_momentum = price_change_pct >= 2.0
    mild_upward_momentum = 0.5 <= price_change_pct < 2.0
    flat_momentum = -0.5 < price_change_pct < 0.5
    mild_downward_momentum = -2.0 < price_change_pct <= -0.5
    strong_downward_momentum = price_change_pct <= -2.0

    # Decision logic
    if strong_positive_sentiment and (mild_upward_momentum or strong_upward_momentum):
        return "STRONG BUY"
    elif mild_positive_sentiment and mild_upward_momentum:
        return "BUY"
    elif strong_negative_sentiment and (mild_downward_momentum or strong_downward_momentum):
        return "STRONG SELL"
    elif mild_negative_sentiment and mild_downward_momentum:
        return "SELL"
    elif neutral_sentiment and flat_momentum:
        return "HOLD"
    elif mild_positive_sentiment and flat_momentum:
        return "WATCHLIST - Possible Upside"
    elif mild_negative_sentiment and flat_momentum:
        return "WATCHLIST - Caution"
    else:
        return "HOLD"
