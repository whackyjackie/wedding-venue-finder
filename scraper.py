"""Web scraper for wedding venue research."""
import time
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from database import VenueDatabase


class VenueScraper:
    """Scrapes Reddit and web for venue information."""

    def __init__(self, db: VenueDatabase, rate_limit_delay: float = 2.5):
        self.db = db
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        time.sleep(self.rate_limit_delay)

    def search_reddit_for_venue(self, venue_name: str, venue_id: int) -> int:
        """
        Search Reddit for mentions of a specific venue.
        Returns number of mentions found.
        """
        query = f"site:reddit.com {venue_name} wedding"
        cached = self.db.get_cached_search(query)

        if cached:
            print(f"Using cached results for: {venue_name}")
            self._save_reddit_results(venue_id, cached)
            return len(cached)

        try:
            results = self._google_search(query)
            self._save_reddit_results(venue_id, results)
            self.db.cache_search(query, results)
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
            query = f"site:reddit.com wedding venue {term}"
            cached = self.db.get_cached_search(query)

            if cached:
                print(f"Using cached results for: {term}")
                all_results.extend(cached)
                continue

            try:
                results = self._google_search(query, max_results=10)
                all_results.extend(results)
                self.db.cache_search(query, results)
                self._rate_limit()
            except Exception as e:
                print(f"Error searching for {term}: {e}")

        return all_results

    def _google_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform Google search and extract Reddit results.
        This is a basic implementation - for production, consider using Google Custom Search API.
        """
        print(f"Searching: {query}")

        # Use DuckDuckGo HTML search as a fallback to Google (no API key needed)
        # For better results, users can implement Google Custom Search API
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

        try:
            self._rate_limit()
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            results = []
            # Basic parsing - this is simplified
            # In practice, you'd want more robust HTML parsing
            lines = response.text.split('\n')

            for i, line in enumerate(lines):
                if 'reddit.com' in line and 'comments' in line:
                    # Try to extract title and URL
                    # This is a basic implementation
                    result = {
                        'title': f'Reddit discussion about {query.split()[-1]}',
                        'url': self._extract_url(line),
                        'snippet': ''
                    }
                    if result['url']:
                        results.append(result)

                if len(results) >= max_results:
                    break

            return results

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return []

    def _extract_url(self, html_line: str) -> Optional[str]:
        """Extract URL from HTML line."""
        try:
            if 'reddit.com' in html_line:
                start = html_line.find('reddit.com')
                if start != -1:
                    # Find the end of the URL
                    end = html_line.find('"', start)
                    if end == -1:
                        end = html_line.find("'", start)
                    if end != -1:
                        url_part = html_line[start:end]
                        return f"https://{url_part}"
        except Exception:
            pass
        return None

    def _save_reddit_results(self, venue_id: int, results: List[Dict[str, Any]]):
        """Save Reddit search results to database."""
        for result in results:
            self.db.add_reddit_mention(
                venue_id=venue_id,
                thread_title=result.get('title', 'No title'),
                url=result.get('url', ''),
                key_quotes=result.get('snippet', '')
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
            # Search for reviews on multiple platforms
            searches = [
                f"{venue_name} site:theknot.com",
                f"{venue_name} site:weddingwire.com",
                f"{venue_name} {venue_location} wedding review"
            ]

            all_results = []
            for search_query in searches:
                results = self._google_search(search_query, max_results=3)
                all_results.extend(results)
                self._rate_limit()

            # Create summary
            summary = self._create_review_summary(all_results)
            self.db.cache_search(f"reviews_{query}", summary)

            return summary

        except Exception as e:
            return f"Error searching for reviews: {e}"

    def _create_review_summary(self, results: List[Dict[str, Any]]) -> str:
        """Create a text summary of review results."""
        if not results:
            return "No reviews found"

        summary_lines = ["Found reviews on:"]
        for result in results:
            url = result.get('url', 'No URL')
            title = result.get('title', 'No title')
            summary_lines.append(f"- {title}")
            summary_lines.append(f"  {url}")

        return "\n".join(summary_lines)


class EnhancedScraper(VenueScraper):
    """
    Enhanced scraper that can use Google Custom Search API if available.
    Set GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables to use.
    """

    def __init__(self, db: VenueDatabase, rate_limit_delay: float = 2.5,
                 google_api_key: Optional[str] = None,
                 google_cse_id: Optional[str] = None):
        super().__init__(db, rate_limit_delay)
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id

    def _google_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Use Google Custom Search API if available, otherwise fallback."""
        if self.google_api_key and self.google_cse_id:
            return self._google_api_search(query, max_results)
        return super()._google_search(query, max_results)

    def _google_api_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform Google search using Custom Search API."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': query,
            'num': min(max_results, 10)
        }

        try:
            self._rate_limit()
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })

            return results

        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return []
