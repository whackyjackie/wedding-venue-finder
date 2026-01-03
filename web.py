#!/usr/bin/env python3
"""Web interface for wedding venue finder."""
from flask import Flask, render_template, request, jsonify, send_file
from database import VenueDatabase
from scraper import VenueScraper
import csv
import io


app = Flask(__name__)
db = VenueDatabase()


@app.route('/')
def index():
    """Home page with venue list."""
    region = request.args.get('region')
    min_capacity = request.args.get('min_capacity', type=int)
    accommodations = request.args.get('accommodations')

    venues = db.search_venues(
        region=region if region else None,
        min_capacity=min_capacity,
        accommodations=accommodations if accommodations else None
    )

    regions = ['NorCal', 'Washington', 'San Juan Islands']
    accommodation_options = ['yes', 'no', 'nearby']

    return render_template('index.html',
                         venues=venues,
                         regions=regions,
                         accommodation_options=accommodation_options,
                         current_region=region,
                         current_capacity=min_capacity,
                         current_accommodations=accommodations)


@app.route('/venue/<int:venue_id>')
def venue_detail(venue_id):
    """Detailed venue page."""
    venue = db.get_venue(venue_id)

    if not venue:
        return "Venue not found", 404

    reddit_mentions = db.get_reddit_mentions(venue_id)

    return render_template('venue_detail.html',
                         venue=venue,
                         reddit_mentions=reddit_mentions)


@app.route('/api/scrape-reddit/<int:venue_id>', methods=['POST'])
def api_scrape_reddit(venue_id):
    """API endpoint to scrape Reddit for a venue."""
    venue = db.get_venue(venue_id)

    if not venue:
        return jsonify({'error': 'Venue not found'}), 404

    try:
        scraper = VenueScraper(db)
        count = scraper.search_reddit_for_venue(venue['name'], venue_id)
        return jsonify({'success': True, 'mentions_found': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-reviews/<int:venue_id>', methods=['POST'])
def api_search_reviews(venue_id):
    """API endpoint to search for venue reviews."""
    venue = db.get_venue(venue_id)

    if not venue:
        return jsonify({'error': 'Venue not found'}), 404

    try:
        scraper = VenueScraper(db)
        summary = scraper.search_venue_reviews(venue['name'], venue['location'])
        db.update_venue(venue_id, review_summary=summary)
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/export')
def export_csv():
    """Export venues to CSV."""
    venues = db.get_all_venues()

    output = io.StringIO()
    fieldnames = ['id', 'name', 'location', 'region', 'website', 'capacity',
                 'overnight_accommodations', 'price_range', 'multi_day_available',
                 'notes', 'review_summary']

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for venue in venues:
        row = {k: venue.get(k, '') for k in fieldnames}
        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='wedding_venues.csv'
    )


@app.route('/stats')
def stats():
    """Statistics page."""
    all_venues = db.get_all_venues()

    stats_data = {
        'total': len(all_venues),
        'by_region': {},
        'by_accommodations': {},
        'avg_capacity': 0
    }

    total_capacity = 0
    for venue in all_venues:
        # Count by region
        region = venue['region']
        stats_data['by_region'][region] = stats_data['by_region'].get(region, 0) + 1

        # Count by accommodations
        acc = venue['overnight_accommodations']
        stats_data['by_accommodations'][acc] = stats_data['by_accommodations'].get(acc, 0) + 1

        # Sum capacity
        if venue['capacity']:
            total_capacity += venue['capacity']

    if all_venues:
        stats_data['avg_capacity'] = total_capacity // len(all_venues)

    return render_template('stats.html', stats=stats_data)


def run_web_server(host='127.0.0.1', port=5000, debug=True):
    """Run the Flask web server."""
    print(f"\n🎉 Wedding Venue Finder Web Interface")
    print(f"=" * 60)
    print(f"Server running at: http://{host}:{port}")
    print(f"Press Ctrl+C to stop")
    print(f"=" * 60)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_web_server()
