"""Web scraper for wedding venue research."""
import time
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from database import VenueDatabase


class VenueScraper:
    """Scrapes Reddit and web for venue information."""

    def __init__(self, db: VenueDatabase, rate_limit_delay: float = 2.0):
        self.db = db
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WeddingVenueFinder/1.0 (Wedding planning research tool)'
        })

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        time.sleep(self.rate_limit_delay)

    def search_reddit_for_venue(self, venue_name: str, venue_id: int) -> int:
        """
        Search Reddit for mentions of a specific venue.
        Returns number of mentions found.
        """
        query = f"{venue_name} wedding"
        cached = self.db.get_cached_search(f"reddit_{query}")

        if cached:
            print(f"Using cached results for: {venue_name}")
            self._save_reddit_results(venue_id, cached)
            return len(cached)

        try:
            results = self._search_reddit_api(query)
            self._save_reddit_results(venue_id, results)
            self.db.cache_search(f"reddit_{query}", results)
            return len(results)
        except Exception as e:
            print(f"Error searching for {venue_name}: {e}")
            return 0

    def search_reddit_for_region(self, region: str) -> List[Dict[str, Any]]:
        """
        Search Reddit for general wedding venue discussions in a region.
        Returns list of relevant threads.
        """
        search_terms = {
            'NorCal': ['Northern California', 'NorCal', 'Bay Area', 'Napa', 'Carmel'],
            'Washington': ['Washington state', 'Seattle', 'Pacific Northwest', 'PNW'],
            'San Juan Islands': ['San Juan Islands', 'Friday Harbor', 'Orcas Island']
        }

        all_results = []
        terms = search_terms.get(region, [region])

        for term in terms:
            query = f"wedding venue {term}"
            cached = self.db.get_cached_search(f"reddit_region_{query}")

            if cached:
                print(f"Using cached results for: {term}")
                all_results.extend(cached)
                continue

            try:
                results = self._search_reddit_api(query, max_results=10)
                all_results.extend(results)
                self.db.cache_search(f"reddit_region_{query}", results)
                self._rate_limit()
            except Exception as e:
                print(f"Error searching for {term}: {e}")

        return all_results

    def _search_reddit_api(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search Reddit using the public JSON API.
        Searches wedding-related subreddits.
        """
        print(f"Searching Reddit for: {query}")

        # Wedding-related subreddits
        subreddits = [
            'weddingplanning',
            'wedding',
            'Weddingsunder10k',
            'weddingvenue',
            'WeddingPhotography'
        ]

        all_results = []
        encoded_query = quote_plus(query)

        for subreddit in subreddits:
            try:
                # Use Reddit's JSON API
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': query,
                    'restrict_sr': '1',  # Restrict to this subreddit
                    'limit': max_results,
                    'sort': 'relevance'
                }

                self._rate_limit()
                response = self.session.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    # Extract posts from Reddit's JSON structure
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children']:
                            post_data = post['data']

                            # Filter out deleted/removed posts
                            if post_data.get('removed_by_category') or post_data.get('author') == '[deleted]':
                                continue

                            result = {
                                'title': post_data.get('title', 'No title'),
                                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                'snippet': self._create_snippet(post_data),
                                'score': post_data.get('score', 0),
                                'num_comments': post_data.get('num_comments', 0),
                                'subreddit': post_data.get('subreddit', '')
                            }
                            all_results.append(result)

                elif response.status_code == 429:
                    print(f"Rate limited by Reddit. Waiting longer...")
                    time.sleep(5)
                else:
                    print(f"Reddit API returned status {response.status_code} for r/{subreddit}")

            except Exception as e:
                print(f"Error searching r/{subreddit}: {e}")
                continue

        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)

        # Sort by score (most upvoted first)
        unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)

        return unique_results[:max_results]

    def _create_snippet(self, post_data: Dict[str, Any]) -> str:
        """Create a snippet from Reddit post data."""
        snippets = []

        # Try selftext first (for text posts)
        selftext = post_data.get('selftext', '').strip()
        if selftext and selftext != '[removed]' and selftext != '[deleted]':
            # Take first 200 characters
            snippet = selftext[:200]
            if len(selftext) > 200:
                snippet += '...'
            snippets.append(snippet)

        # Add score and comments info
        score = post_data.get('score', 0)
        comments = post_data.get('num_comments', 0)
        snippets.append(f"{score} upvotes, {comments} comments")

        return ' | '.join(snippets) if snippets else ''

    def _save_reddit_results(self, venue_id: int, results: List[Dict[str, Any]]):
        """Save Reddit search results to database."""
        for result in results:
            # Create a more detailed quote including metadata
            quote_parts = []
            if result.get('snippet'):
                quote_parts.append(result['snippet'])
            if result.get('subreddit'):
                quote_parts.append(f"Posted in r/{result['subreddit']}")

            key_quotes = ' | '.join(quote_parts) if quote_parts else None

            self.db.add_reddit_mention(
                venue_id=venue_id,
                thread_title=result.get('title', 'No title'),
                url=result.get('url', ''),
                key_quotes=key_quotes
            )

    def search_venue_reviews(self, venue_name: str, venue_location: str) -> str:
        """
        Search for venue reviews across the web.
        Returns a summary of findings.
        """
        query = f"{venue_name} {venue_location} wedding reviews"
        cached = self.db.get_cached_search(f"reviews_{query}")

        if cached:
            return cached

        try:
            # Also search Reddit for this specific venue
            reddit_query = f"{venue_name} review"
            reddit_results = self._search_reddit_api(reddit_query, max_results=5)

            # Create summary
            summary = self._create_review_summary(reddit_results, venue_name)
            self.db.cache_search(f"reviews_{query}", summary)

            return summary

        except Exception as e:
            return f"Error searching for reviews: {e}"

    def _create_review_summary(self, results: List[Dict[str, Any]], venue_name: str) -> str:
        """Create a text summary of review results."""
        if not results:
            return f"No Reddit reviews found for {venue_name}. Try searching wedding review sites like TheKnot.com or WeddingWire.com directly."

        summary_lines = [f"Found {len(results)} Reddit mention(s):\n"]

        for result in results:
            summary_lines.append(f"• {result.get('title', 'No title')}")
            summary_lines.append(f"  {result.get('url', 'No URL')}")
            summary_lines.append(f"  {result.get('score', 0)} upvotes, {result.get('num_comments', 0)} comments")
            if result.get('snippet'):
                # Clean up snippet
                snippet = result['snippet'].replace('\n', ' ')[:150]
                summary_lines.append(f"  \"{snippet}...\"")
            summary_lines.append("")

        summary_lines.append("For more reviews, check:")
        summary_lines.append(f"• TheKnot.com: Search '{venue_name}'")
        summary_lines.append(f"• WeddingWire.com: Search '{venue_name}'")
        summary_lines.append(f"• Google Reviews: Search '{venue_name} reviews'")

        return "\n".join(summary_lines)


class EnhancedScraper(VenueScraper):
    """
    Enhanced scraper that can use Google Custom Search API if available.
    Set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables to use.
    """

    def __init__(self, db: VenueDatabase, rate_limit_delay: float = 2.0,
                 google_api_key: Optional[str] = None,
                 google_cse_id: Optional[str] = None):
        super().__init__(db, rate_limit_delay)
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
