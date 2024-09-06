from . import params
from newsapi import NewsApiClient

def denewline(line: str) -> str:
    return line.replace("\n", "")

def search_news(query):
    from newsapi import NewsApiClient

    api = NewsApiClient(api_key=params.NEWS_API_KEY)
    results = api.get_everything(q=query)

    return "\n".join(
        [
            f'- {denewline(article["title"])}: {denewline(article["description"])}'  # noqa: E501
            for article in results["articles"]
            if article["title"]
            and article["description"]
            and article["title"] != "[Removed]"
        ][:10]
    )
