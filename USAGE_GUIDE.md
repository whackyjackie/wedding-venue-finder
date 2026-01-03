# Quick Usage Guide

## Getting Started

1. **Quick setup** (first time only):
```bash
./quickstart.sh
```

OR do it manually:
```bash
pip3 install -r requirements.txt
python3 seed_data.py
```

## Common Tasks

### Browse Venues

**Web Interface (Recommended for browsing):**
```bash
python3 web.py
```
Then open: http://127.0.0.1:5000

**Command Line:**
```bash
# List all venues
python3 cli.py list

# Filter by region
python3 cli.py list --region "San Juan Islands"

# Filter by capacity (minimum 125 guests)
python3 cli.py list --capacity 125

# Filter by overnight accommodations
python3 cli.py list --accommodations yes

# Combine filters
python3 cli.py list --region NorCal --capacity 150 --accommodations yes
```

### View Venue Details

```bash
# View basic info
python3 cli.py view 1

# View with Reddit discussions
python3 cli.py view 1 --reddit
```

### Research a Venue

**Option 1: Use Web Interface**
1. Start web server: `python3 web.py`
2. Click on a venue
3. Click "Search Reddit" button
4. Click "Search Reviews" button

**Option 2: Use CLI**
```bash
# Search Reddit for specific venue
python3 cli.py scrape-reddit --venue-id 1

# Search for reviews
python3 cli.py search-reviews --venue-id 1

# View updated info
python3 cli.py view 1 --reddit
```

### Add Custom Venues

```bash
python3 cli.py add
```
Follow the interactive prompts.

### Export Data

**Web Interface:**
- Visit http://127.0.0.1:5000/export

**Command Line:**
```bash
python3 cli.py export my_venues.csv
```

## Workflow Recommendations

### Initial Setup & Bulk Research
1. Run `python3 seed_data.py` to populate database
2. Use CLI to scrape Reddit for all venues:
   ```bash
   python3 cli.py scrape-reddit
   ```
   (This will take time due to rate limiting - be patient!)
3. Search reviews for venues you're most interested in

### Daily Browsing & Comparison
1. Start web server: `python3 web.py`
2. Use filters to narrow down options
3. Click through venues to compare
4. Take notes in the web interface or via CLI

### Adding Research Notes
```bash
# View a venue to get its ID
python3 cli.py list

# Use your preferred text editor or the CLI
# (Note: Update functionality can be added via the database.py API)
```

### Final Decision Making
1. Export filtered results to CSV
2. Open in spreadsheet software
3. Share with partner/family for feedback

## Tips

- **Start broad, then narrow**: Begin with all venues, then filter by region and capacity
- **Use caching**: Search results are cached for 24 hours - repeated searches are instant
- **Be patient with scraping**: Rate limiting means bulk scraping takes time
- **Export often**: Keep CSV backups of your research
- **Mix interfaces**: Use CLI for data collection, web for comparison

## Quick Reference

| Task | CLI Command | Web Interface |
|------|-------------|---------------|
| Browse all venues | `cli.py list` | Visit `/` |
| Filter by region | `cli.py list --region NorCal` | Use dropdown |
| View details | `cli.py view 1` | Click venue name |
| Search Reddit | `cli.py scrape-reddit --venue-id 1` | Click button |
| Search reviews | `cli.py search-reviews --venue-id 1` | Click button |
| Add venue | `cli.py add` | _(CLI only)_ |
| Export | `cli.py export file.csv` | Visit `/export` |
| Statistics | _(N/A)_ | Visit `/stats` |

## Troubleshooting

**"No module named 'requests'"**
```bash
pip3 install -r requirements.txt
```

**"No such file: data/venues.db"**
```bash
python3 seed_data.py
```

**Web server won't start**
- Check if port 5000 is in use
- Try: `python3 web.py` to see error messages

**Scraping finds no results**
- This is expected with DuckDuckGo's basic search
- Results may be limited
- Consider setting up Google Custom Search API (see README.md)
