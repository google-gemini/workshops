# Copyright 2025 Google LLC
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

"""Comprehensive film data gathering for embedding creation

Combines TMDB structured data with Wikipedia contextual articles
to create rich film knowledge documents.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional

from .tmdb_client import search_movie_with_credits
from .wikipedia_client import get_wikipedia_article


async def gather_cast_articles(cast_list) -> List[Dict]:
    """Get Wikipedia articles for ALL cast members

    Args:
        cast_list: TMDB cast list

    Returns:
        List of cast member data with Wikipedia articles
    """
    articles = []

    print(f"🎭 Gathering cast data for {len(cast_list)} actors...")

    for i, actor in enumerate(cast_list, 1):
        print(f"  {i}/{len(cast_list)}: {actor.name} ({actor.character})")

        try:
            article = await get_wikipedia_article(actor.name, "person")
            if article and article.get("full_text"):
                articles.append(
                    {"name": actor.name, "character": actor.character, "billing_order": i, "article": article}
                )
                print(f"    ✅ Got {len(article['full_text'])} characters")
            else:
                print(f"    ⚠️ No Wikipedia article found")

        except Exception as e:
            print(f"    ❌ Error: {e}")

        # Small delay to be respectful to Wikipedia
        await asyncio.sleep(0.5)

    print(f"📊 Successfully gathered {len(articles)}/{len(cast_list)} cast articles")
    return articles


async def gather_crew_articles(crew_list) -> List[Dict]:
    """Get Wikipedia articles for ALL crew members

    Args:
        crew_list: TMDB crew list

    Returns:
        List of crew member data with Wikipedia articles
    """
    # Get unique crew members (avoid duplicates like same person in multiple roles)
    unique_crew = {}
    for crew_member in crew_list:
        # Use name as key to avoid duplicate people in multiple roles
        if crew_member.name not in unique_crew:
            unique_crew[crew_member.name] = {"name": crew_member.name, "jobs": [crew_member.job]}
        else:
            unique_crew[crew_member.name]["jobs"].append(crew_member.job)

    articles = []
    crew_members = list(unique_crew.values())

    print(f"🎬 Gathering crew data for {len(crew_members)} key personnel...")

    for i, crew_data in enumerate(crew_members, 1):
        name = crew_data["name"]
        jobs = ", ".join(crew_data["jobs"])
        print(f"  {i}/{len(crew_members)}: {name} ({jobs})")

        try:
            article = await get_wikipedia_article(name, "person")
            if article and article.get("full_text"):
                articles.append({"name": name, "jobs": crew_data["jobs"], "jobs_str": jobs, "article": article})
                print(f"    ✅ Got {len(article['full_text'])} characters")
            else:
                print(f"    ⚠️ No Wikipedia article found")

        except Exception as e:
            print(f"    ❌ Error: {e}")

        # Small delay to be respectful to Wikipedia
        await asyncio.sleep(0.5)

    print(f"📊 Successfully gathered {len(articles)}/{len(crew_members)} crew articles")
    return articles


def format_tmdb_section(movie) -> str:
    """Format TMDB data into readable text section"""
    if not movie:
        return "No TMDB data available.\n"

    sections = []

    # Basic film info
    sections.append(f"Title: {movie.title}")
    sections.append(f"Release Date: {movie.release_date}")
    sections.append(f"Runtime: {movie.runtime} minutes" if movie.runtime else "Runtime: Unknown")

    # Genres
    if movie.genres:
        genres = ", ".join([genre.name for genre in movie.genres])
        sections.append(f"Genres: {genres}")

    # Production companies
    if hasattr(movie, "production_companies") and movie.production_companies:
        companies = ", ".join([company.name for company in movie.production_companies[:3]])
        sections.append(f"Production: {companies}")

    # Plot overview
    if movie.overview:
        sections.append(f"\nPlot Overview:\n{movie.overview}")

    # Cast summary
    if movie.credits and movie.credits.cast:
        sections.append(f"\nMain Cast:")
        for actor in movie.credits.cast[:8]:
            sections.append(f"  • {actor.name} as {actor.character}")

    # Crew summary
    if movie.credits and movie.credits.crew:
        directors = [crew.name for crew in movie.credits.crew if crew.job == "Director"]
        writers = [crew.name for crew in movie.credits.crew if crew.job in ["Writer", "Screenplay"]]

        if directors:
            sections.append(f"\nDirector: {', '.join(directors)}")
        if writers:
            sections.append(f"Writers: {', '.join(writers[:3])}")

    return "\n".join(sections) + "\n"


def format_comprehensive_document(tmdb_data, film_article, cast_articles, crew_articles) -> str:
    """Combine all gathered data into one comprehensive document"""

    title = tmdb_data.title if tmdb_data else "Unknown Film"
    year = tmdb_data.release_date.year if tmdb_data and tmdb_data.release_date else "Unknown"

    doc_sections = []

    # Header
    doc_sections.append(f"{title.upper()} ({year}) - COMPREHENSIVE FILM CONTEXT")
    doc_sections.append("=" * 60)
    doc_sections.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc_sections.append("")

    # TMDB structured data
    doc_sections.append("=== FILM OVERVIEW (TMDB DATA) ===")
    doc_sections.append(format_tmdb_section(tmdb_data))

    # Wikipedia film article
    if film_article and film_article.get("full_text"):
        doc_sections.append("=== FILM ANALYSIS (WIKIPEDIA) ===")
        doc_sections.append(f"Source: {film_article.get('title', 'Unknown')}")
        doc_sections.append("")
        doc_sections.append(film_article["full_text"])
        doc_sections.append("")

    # Cast articles
    if cast_articles:
        doc_sections.append("=== CAST BIOGRAPHIES ===")
        for cast_member in cast_articles:
            doc_sections.append(f"--- {cast_member['name']} as {cast_member['character']} ---")
            doc_sections.append("")
            if cast_member["article"].get("full_text"):
                doc_sections.append(cast_member["article"]["full_text"])
            doc_sections.append("")

    # Crew articles
    if crew_articles:
        doc_sections.append("=== CREW BIOGRAPHIES ===")
        for crew_member in crew_articles:
            doc_sections.append(f"--- {crew_member['name']} ({crew_member['jobs_str']}) ---")
            doc_sections.append("")
            if crew_member["article"].get("full_text"):
                doc_sections.append(crew_member["article"]["full_text"])
            doc_sections.append("")

    return "\n".join(doc_sections)


async def gather_comprehensive_film_data(title: str, year: int, output_file: Optional[str] = None) -> str:
    """Gather all available data about a film for embedding creation

    Args:
        title: Film title
        year: Release year
        output_file: Optional file path to save the document

    Returns:
        Comprehensive film document as string
    """

    print(f"🎬 Gathering comprehensive data for '{title}' ({year})")
    print("=" * 60)

    # 1. Get structured TMDB data
    print("📊 Step 1: Getting TMDB data...")
    tmdb_data = search_movie_with_credits(title, year)
    if not tmdb_data:
        print("❌ No TMDB data found - aborting")
        return ""

    # 2. Get film Wikipedia article
    print("\n📖 Step 2: Getting film Wikipedia article...")
    film_article = await get_wikipedia_article(title, "film", year)

    # 3. Get cast Wikipedia articles
    print(f"\n🎭 Step 3: Getting cast articles (all cast)...")
    cast_articles = []
    if tmdb_data.credits and tmdb_data.credits.cast:
        cast_articles = await gather_cast_articles(tmdb_data.credits.cast)

    # 4. Get crew Wikipedia articles
    print(f"\n🎬 Step 4: Getting crew articles...")
    crew_articles = []
    if tmdb_data.credits and tmdb_data.credits.crew:
        crew_articles = await gather_crew_articles(tmdb_data.credits.crew)

    # 5. Format comprehensive document
    print(f"\n📝 Step 5: Formatting comprehensive document...")
    document = format_comprehensive_document(tmdb_data, film_article, cast_articles, crew_articles)

    # 6. Save to file if requested
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(document)
        print(f"💾 Document saved to: {output_file}")

    # Summary stats
    print(f"\n📊 SUMMARY:")
    print(f"   Document length: {len(document):,} characters")
    print(f"   Film article: {'✅' if film_article else '❌'}")
    print(
        f"   Cast articles: {len(cast_articles)} of {len(tmdb_data.credits.cast) if tmdb_data.credits and tmdb_data.credits.cast else 0}"
    )
    print(
        f"   Crew articles: {len(crew_articles)} of {len(tmdb_data.credits.crew) if tmdb_data.credits and tmdb_data.credits.crew else 0}"
    )

    return document


if __name__ == "__main__":
    # Test with The Big Sleep
    import sys

    async def test_data_gathering():
        if len(sys.argv) < 2:
            print("Usage: python data_gatherer.py 'Movie Title' [year]")
            print("Example: python data_gatherer.py 'The Big Sleep' 1946")
            sys.exit(1)

        title = sys.argv[1]
        year = int(sys.argv[2]) if len(sys.argv) > 2 else None

        # Generate output filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).rstrip()
        output_file = f"{safe_title.replace(' ', '_')}_{year}_context.txt"

        try:
            document = await gather_comprehensive_film_data(title, year, output_file)

            if document:
                print(f"\n🎉 Success! Generated comprehensive film context document.")
                print(f"📄 File: {output_file}")
                print(f"📊 Size: {len(document):,} characters")
            else:
                print(f"\n❌ Failed to generate document")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()

    asyncio.run(test_data_gathering())
