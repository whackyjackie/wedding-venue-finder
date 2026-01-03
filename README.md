# Wedding Venue Finder

A comprehensive tool to research and organize wedding venues for a 2-3 day retreat for 125-150 guests in Northern California, Washington, and San Juan Islands.

## Features

- SQLite database for venue information
- Reddit scraper to find venue discussions
- Web search for venue reviews
- CLI interface for data management
- Web interface for browsing and comparing venues
- CSV export functionality
- Intelligent caching to avoid redundant searches
- Rate limiting for respectful web scraping

## Installation

1. Navigate to the project directory:
```bash
cd wedding-venue-finder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database with seed data:
```bash
python seed_data.py
```

## Usage

### CLI Interface

The CLI provides full control over the venue database:

**List all venues:**
```bash
python cli.py list
```

**Filter venues:**
```bash
# By region
python cli.py list --region NorCal

# By minimum capacity
python cli.py list --capacity 150

# By overnight accommodations
python cli.py list --accommodations yes

# Combine filters
python cli.py list --region "San Juan Islands" --capacity 125 --accommodations yes
```

**View venue details:**
```bash
# Basic info
python cli.py view 1

# Include Reddit mentions
python cli.py view 1 --reddit
```

**Add a new venue:**
```bash
python cli.py add
# Follow the interactive prompts
```

**Scrape Reddit for mentions:**
```bash
# For a specific venue
python cli.py scrape-reddit --venue-id 1

# For all venues
python cli.py scrape-reddit
```

**Search for reviews:**
```bash
python cli.py search-reviews --venue-id 1
```

**Export to CSV:**
```bash
# Default filename (venues_export.csv)
python cli.py export

# Custom filename
python cli.py export my_venues.csv
```

### Web Interface

Launch the web server:
```bash
python web.py
```

Then open your browser to: http://127.0.0.1:5000

The web interface provides:
- **Home page**: Browse and filter venues
- **Venue details**: View full information, Reddit mentions, and reviews
- **Statistics**: Overview of your venue database
- **CSV Export**: Download all venues as a spreadsheet
- **Interactive scraping**: Click buttons to search Reddit or reviews

## Database Schema

### Venues Table
- `id`: Primary key
- `name`: Venue name
- `location`: City, State
- `region`: NorCal, Washington, or San Juan Islands
- `website`: Venue URL
- `capacity`: Number of guests
- `overnight_accommodations`: yes, no, or nearby
- `price_range`: $ to $$$$$
- `multi_day_available`: Boolean
- `notes`: Additional information
- `review_summary`: Aggregated review data
- `created_at`, `updated_at`: Timestamps

### Reddit Mentions Table
- `id`: Primary key
- `venue_id`: Foreign key to venues
- `thread_title`: Reddit thread title
- `url`: Link to discussion
- `key_quotes`: Relevant excerpts
- `scraped_at`: Timestamp

### Search Cache Table
- Stores search results with 24-hour TTL
- Prevents redundant API calls

## Initial Venues

The database comes pre-seeded with 14 venues:

**Northern California (6 venues):**
- Carmel Valley Ranch
- Cavallo Point
- Holman Ranch
- Calistoga Ranch
- The Estate Yountville
- Costanoa

**Washington (4 venues):**
- Suncadia Resort
- Chateau Lill
- DeLille Cellars
- Sleeping Lady Mountain Resort

**San Juan Islands (4 venues):**
- Roche Harbor Resort
- Rosario Resort & Spa
- Outlook Inn
- Friday Harbor House

## Rate Limiting

The scraper uses a 2.5-second delay between requests by default. This ensures respectful crawling and reduces the chance of being blocked.

## Search Caching

All search results are cached for 24 hours. This means:
- Faster subsequent searches
- Reduced load on external services
- Lower chance of rate limiting

To clear the cache, simply delete the `data/venues.db` file and re-run `seed_data.py`.

## Tips for Use

1. **Start with seeding**: Run `seed_data.py` to populate your database
2. **Use the web interface for browsing**: It's easier to compare venues visually
3. **Use the CLI for batch operations**: Like scraping Reddit for all venues
4. **Export regularly**: Save CSV backups of your research
5. **Add notes as you research**: Keep track of pros, cons, and important details
6. **Search Reddit incrementally**: Do it venue by venue to monitor progress
7. **Be patient with scraping**: Rate limiting means it takes time, but protects you

## Advanced: Google Custom Search API

For better search results, you can use Google's Custom Search API:

1. Get an API key from Google Cloud Console
2. Create a Custom Search Engine and get the CSE ID
3. Set environment variables:
```bash
export GOOGLE_API_KEY="your_api_key"
export GOOGLE_CSE_ID="your_cse_id"
```

The scraper will automatically use the API if these are set.

## Project Structure

```
wedding-venue-finder/
├── data/
│   └── venues.db          # SQLite database
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Venue list page
│   ├── venue_detail.html  # Venue detail page
│   └── stats.html         # Statistics page
├── database.py            # Database management
├── scraper.py             # Web scraping functionality
├── cli.py                 # Command-line interface
├── web.py                 # Flask web server
├── seed_data.py           # Initial venue data
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Troubleshooting

**Database not found:**
```bash
python seed_data.py
```

**Import errors:**
```bash
pip install -r requirements.txt
```

**Web interface not loading:**
- Check that port 5000 is available
- Try: `python web.py` and look for error messages

**Scraping not finding results:**
- This is normal - DuckDuckGo search is basic
- Consider setting up Google Custom Search API
- Results are cached, so you may be seeing old data

## Future Enhancements

Possible improvements:
- Booking availability calendar
- Cost calculator for multi-day events
- Photo galleries
- Venue comparison tool
- Email alerts for new Reddit mentions
- Integration with wedding planning tools
- Map view of venues
- Weather data for planning

## License

Personal use for wedding planning research.
