"""TMDB API client for film data retrieval"""

import os
from themoviedb import TMDb


def search_movie_with_credits(title: str, year: int = None):
    """Search for a movie and return first result with full cast/crew
    
    Args:
        title: Movie title to search for
        year: Optional year to filter results
        
    Returns:
        Movie object with credits attached, or None if not found
    """
    
    # Initialize TMDB client
    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        raise ValueError("TMDB_API_KEY environment variable not set")
    
    tmdb = TMDb(key=api_key)
    
    # Search for the movie
    print(f"🔍 Searching TMDB for '{title}'{f' ({year})' if year else ''}")
    search_results = tmdb.search().movies(title)
    
    if not search_results:
        print(f"❌ No movies found for '{title}'")
        return None
    
    # Filter by year if provided
    if year:
        year_filtered = [
            movie for movie in search_results 
            if movie.release_date and movie.release_date.year == year
        ]
        if year_filtered:
            first_result = year_filtered[0]
            print(f"✅ Found year match: {first_result.title} ({first_result.release_date})")
        else:
            print(f"⚠️ No movies found for '{title}' in {year}, using first result")
            first_result = search_results[0]
            print(f"📽️ Using: {first_result.title} ({first_result.release_date})")
    else:
        first_result = search_results[0]
        print(f"📽️ Found: {first_result.title} ({first_result.release_date})")
    
    # Get full details with credits
    print(f"📊 Fetching detailed information with cast/crew...")
    movie_details = tmdb.movie(first_result.id).details(
        append_to_response="credits"
    )
    
    print(f"✅ Retrieved movie data:")
    print(f"   Title: {movie_details.title}")
    print(f"   Year: {movie_details.release_date}")
    print(f"   Cast: {len(movie_details.credits.cast) if movie_details.credits else 0} actors")
    print(f"   Crew: {len(movie_details.credits.crew) if movie_details.credits else 0} crew members")
    
    return movie_details


def format_movie_summary(movie):
    """Format movie data into readable summary"""
    if not movie:
        return "No movie data available"
    
    summary = []
    
    # Basic info
    summary.append(f"**{movie.title}** ({movie.release_date.year if movie.release_date else 'Unknown'})")
    summary.append(f"Runtime: {movie.runtime} minutes" if movie.runtime else "Runtime: Unknown")
    
    # Genres
    if movie.genres:
        genres = ", ".join([genre.name for genre in movie.genres])
        summary.append(f"Genres: {genres}")
    
    # Plot
    if movie.overview:
        summary.append(f"\nPlot: {movie.overview}")
    
    # Director
    if movie.credits and movie.credits.crew:
        directors = [crew.name for crew in movie.credits.crew if crew.job == "Director"]
        if directors:
            summary.append(f"Director: {', '.join(directors)}")
    
    # Top cast
    if movie.credits and movie.credits.cast:
        top_cast = movie.credits.cast[:5]  # Top 5 billing
        cast_info = []
        for actor in top_cast:
            cast_info.append(f"{actor.name} as {actor.character}")
        summary.append(f"\nTop Cast:")
        summary.extend([f"  - {info}" for info in cast_info])
    
    return "\n".join(summary)


if __name__ == "__main__":
    # Test functionality independently
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tmdb_client.py 'Movie Title' [year]")
        print("Example: python tmdb_client.py 'The Big Sleep' 1946")
        sys.exit(1)
    
    title = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    try:
        movie = search_movie_with_credits(title, year)
        if movie:
            print("\n" + "="*50)
            print("MOVIE SUMMARY")
            print("="*50)
            print(format_movie_summary(movie))
            
            # Show some specific credits for debugging
            if movie.credits:
                print(f"\n📝 Sample cast members:")
                for actor in movie.credits.cast[:3]:
                    print(f"   {actor.name} ({actor.character})")
                    
                print(f"\n🎬 Sample crew members:")
                key_crew = [crew for crew in movie.credits.crew if crew.job in ["Director", "Producer", "Writer"]]
                for crew in key_crew[:5]:
                    print(f"   {crew.name} ({crew.job})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
