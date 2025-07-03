from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text: str):
    score = analyzer.polarity_scores(text)
    return score["compound"]

def analyze_news_sentiment(news_list):
    if not news_list:
        return 0.0

    valid_scores = []
    for article in news_list:
        # Combine title and summary if available
        text = ""
        if isinstance(article, dict):
            text = article.get("title") or article.get("headline") or ""
            summary = article.get("summary", "")
            text += f" {summary}".strip()
        elif isinstance(article, str):
            text = article

        if not text.strip() or "No recent news found." in text or "Error" in text:
            continue

        score = get_sentiment(text)
        valid_scores.append(score)

    return sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
