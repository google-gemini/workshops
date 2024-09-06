# Copyright 2024 -l
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
