"""Wikipedia API client for film and person data retrieval"""

import asyncio
import aiohttp
from urllib.parse import quote


async def fetch_wikipedia_direct(title: str) -> dict:
    """Fetch Wikipedia article directly by title
    
    Args:
        title: Exact Wikipedia article title
        
    Returns:
        Dictionary with article data or None if not found
    """
    # Use Wikipedia REST API for summary
    encoded_title = quote(title.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if it's a disambiguation page or redirect
                    if data.get('type') == 'disambiguation':
                        print(f"⚠️ '{title}' is a disambiguation page")
                        return None
                    
                    print(f"✅ Found Wikipedia article: {data.get('title')}")
                    return data
                    
                elif response.status == 404:
                    print(f"❌ Wikipedia article '{title}' not found")
                    return None
                else:
                    print(f"⚠️ Wikipedia API error {response.status} for '{title}'")
                    return None
                    
    except Exception as e:
        print(f"❌ Error fetching Wikipedia article '{title}': {e}")
        return None


async def search_wikipedia(query: str) -> list:
    """Search Wikipedia and return list of matching titles
    
    Args:
        query: Search query
        
    Returns:
        List of matching article titles
    """
    encoded_query = quote(query)
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded_query}&limit=5&format=json"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # OpenSearch API returns [query, [titles], [descriptions], [urls]]
                    titles = data[1] if len(data) > 1 else []
                    print(f"🔍 Wikipedia search for '{query}' found {len(titles)} results")
                    return titles
                else:
                    print(f"⚠️ Wikipedia search API error {response.status}")
                    return []
                    
    except Exception as e:
        print(f"❌ Error searching Wikipedia for '{query}': {e}")
        return []


async def fetch_full_wikipedia_text(title: str) -> str:
    """Fetch full Wikipedia article text (not just summary)
    
    Args:
        title: Wikipedia article title
        
    Returns:
        Full article text or empty string if not found
    """
    encoded_title = quote(title.replace(" ", "_"))
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={encoded_title}&prop=extracts&format=json&exsectionformat=plain&explaintext=true"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    pages = data.get('query', {}).get('pages', {})
                    
                    for page_id, page_data in pages.items():
                        if page_id != '-1':  # -1 means page not found
                            extract = page_data.get('extract', '')
                            print(f"📄 Retrieved full text for '{title}' ({len(extract)} characters)")
                            return extract
                    
                    print(f"❌ No full text found for '{title}'")
                    return ""
                else:
                    print(f"⚠️ Wikipedia extract API error {response.status}")
                    return ""
                    
    except Exception as e:
        print(f"❌ Error fetching full Wikipedia text for '{title}': {e}")
        return ""


def format_wikipedia_title(name: str, content_type: str, year: int = None) -> str:
    """Format a name into a likely Wikipedia article title
    
    Args:
        name: Name of person or film
        content_type: 'film' or 'person'
        year: Year for films
        
    Returns:
        Formatted Wikipedia title
    """
    if content_type == "film":
        if year:
            return f"{name} ({year} film)"
        else:
            return name
    elif content_type == "person":
        return name
    else:
        return name


async def get_wikipedia_article(name: str, content_type: str = "person", year: int = None) -> dict:
    """Get Wikipedia article with direct access + search fallback
    
    Args:
        name: Name to search for
        content_type: 'film' or 'person'
        year: Year for films
        
    Returns:
        Dictionary with Wikipedia data or None if not found
    """
    print(f"🔍 Getting Wikipedia article for '{name}' ({content_type})")
    
    # Try direct access first
    direct_title = format_wikipedia_title(name, content_type, year)
    result = await fetch_wikipedia_direct(direct_title)
    
    if result:
        # Get full text for the article
        full_text = await fetch_full_wikipedia_text(result['title'])
        result['full_text'] = full_text
        return result
    
    # Fallback to search
    print(f"🔍 Direct access failed, searching for '{name}'...")
    search_results = await search_wikipedia(name)
    
    if search_results:
        # Try the first search result
        first_result_title = search_results[0]
        print(f"📖 Trying first search result: '{first_result_title}'")
        
        result = await fetch_wikipedia_direct(first_result_title)
        if result:
            # Get full text for the article
            full_text = await fetch_full_wikipedia_text(result['title'])
            result['full_text'] = full_text
            return result
    
    print(f"❌ No Wikipedia article found for '{name}'")
    return None


def format_wikipedia_summary(article_data: dict) -> str:
    """Format Wikipedia article data into readable summary
    
    Args:
        article_data: Data returned from get_wikipedia_article
        
    Returns:
        Formatted text summary
    """
    if not article_data:
        return "No Wikipedia data available"
    
    summary = []
    summary.append(f"**{article_data.get('title', 'Unknown')}**")
    
    if article_data.get('description'):
        summary.append(f"Description: {article_data['description']}")
    
    if article_data.get('extract'):
        # Use the summary extract (shorter)
        summary.append(f"\nSummary: {article_data['extract']}")
    
    # Full text is available in article_data['full_text'] for embedding purposes
    
    return "\n".join(summary)


if __name__ == "__main__":
    # Test functionality independently
    import sys
    
    async def test_wikipedia_client():
        if len(sys.argv) < 2:
            print("Usage: python wikipedia_client.py 'Query' [type] [year]")
            print("Examples:")
            print("  python wikipedia_client.py 'Humphrey Bogart' person")
            print("  python wikipedia_client.py 'The Big Sleep' film 1946")
            sys.exit(1)
        
        query = sys.argv[1]
        content_type = sys.argv[2] if len(sys.argv) > 2 else "person"
        year = int(sys.argv[3]) if len(sys.argv) > 3 else None
        
        try:
            article = await get_wikipedia_article(query, content_type, year)
            if article:
                print("\n" + "="*50)
                print("WIKIPEDIA SUMMARY")
                print("="*50)
                print(format_wikipedia_summary(article))
                
                if article.get('full_text'):
                    print(f"\n📊 Full article length: {len(article['full_text'])} characters")
                    print(f"First 200 chars: {article['full_text'][:200]}...")
            else:
                print("No Wikipedia article found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(test_wikipedia_client())
