from newsapi import NewsApiClient

from . import params


def denewline(line: str) -> str:
    return line.replace("\n", "")


def search_news(query):
    api = NewsApiClient(api_key=params.NEWS_API_KEY)
    results = api.get_everything(q=query)

    return "\n".join(
        [
            f'- {denewline(article["title"])}: {denewline(article["description"])} ({article["url"]})'  # noqa: E501
            for article in results["articles"]
            if article["title"]
            and article["description"]
            and article["title"] != "[Removed]"
        ][:10]
    )
