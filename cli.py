#!/usr/bin/env python3
"""Command-line interface for wedding venue finder."""
import sys
import argparse
from database import VenueDatabase
from scraper import VenueScraper
import csv


def list_venues(db: VenueDatabase, region=None, min_capacity=None, accommodations=None):
    """List venues with optional filters."""
    venues = db.search_venues(region=region, min_capacity=min_capacity, accommodations=accommodations)

    if not venues:
        print("No venues found matching criteria.")
        return

    print(f"\nFound {len(venues)} venue(s):\n")
    print("-" * 100)

    for venue in venues:
        print(f"ID: {venue['id']}")
        print(f"Name: {venue['name']}")
        print(f"Location: {venue['location']} ({venue['region']})")
        print(f"Capacity: {venue['capacity']} guests")
        print(f"Overnight: {venue['overnight_accommodations']}")
        print(f"Price: {venue['price_range']}")
        print(f"Multi-day: {'Yes' if venue['multi_day_available'] else 'No'}")
        if venue['website']:
            print(f"Website: {venue['website']}")
        if venue['notes']:
            print(f"Notes: {venue['notes']}")
        print("-" * 100)


def view_venue(db: VenueDatabase, venue_id: int, show_reddit: bool = False):
    """View detailed information about a venue."""
    venue = db.get_venue(venue_id)

    if not venue:
        print(f"Venue ID {venue_id} not found.")
        return

    print("\n" + "=" * 100)
    print(f"{venue['name']}")
    print("=" * 100)
    print(f"Location: {venue['location']}")
    print(f"Region: {venue['region']}")
    print(f"Capacity: {venue['capacity']} guests")
    print(f"Overnight Accommodations: {venue['overnight_accommodations']}")
    print(f"Price Range: {venue['price_range']}")
    print(f"Multi-day Available: {'Yes' if venue['multi_day_available'] else 'No'}")

    if venue['website']:
        print(f"Website: {venue['website']}")

    if venue['notes']:
        print(f"\nNotes:\n{venue['notes']}")

    if venue['review_summary']:
        print(f"\nReviews:\n{venue['review_summary']}")

    if show_reddit:
        mentions = db.get_reddit_mentions(venue_id)
        if mentions:
            print(f"\n{'=' * 100}")
            print(f"Reddit Mentions ({len(mentions)}):")
            print("=" * 100)
            for mention in mentions:
                print(f"\nTitle: {mention['thread_title']}")
                print(f"URL: {mention['url']}")
                if mention['key_quotes']:
                    print(f"Quotes: {mention['key_quotes']}")
                print("-" * 100)
        else:
            print("\nNo Reddit mentions found. Run 'scrape-reddit' to search.")

    print()


def add_venue(db: VenueDatabase):
    """Interactive venue addition."""
    print("\n=== Add New Venue ===\n")

    name = input("Venue name: ").strip()
    location = input("Location (City, State): ").strip()

    print("\nRegion options: NorCal, Washington, San Juan Islands")
    region = input("Region: ").strip()

    if region not in ['NorCal', 'Washington', 'San Juan Islands']:
        print("Invalid region. Please use: NorCal, Washington, or San Juan Islands")
        return

    website = input("Website (optional): ").strip() or None

    try:
        capacity = int(input("Capacity (number of guests): ").strip())
    except ValueError:
        print("Invalid capacity. Please enter a number.")
        return

    print("\nOvernight accommodations: yes, no, nearby")
    overnight = input("Overnight accommodations: ").strip() or None

    price_range = input("Price range ($-$$$$$, optional): ").strip() or None

    multi_day = input("Multi-day available? (y/n): ").strip().lower()
    multi_day_available = multi_day == 'y'

    notes = input("Notes (optional): ").strip() or None

    try:
        venue_id = db.add_venue(
            name=name,
            location=location,
            region=region,
            website=website,
            capacity=capacity,
            overnight_accommodations=overnight,
            price_range=price_range,
            multi_day_available=multi_day_available,
            notes=notes
        )
        print(f"\n✓ Venue added successfully! ID: {venue_id}")
    except Exception as e:
        print(f"\n✗ Error adding venue: {e}")


def scrape_reddit_mentions(db: VenueDatabase, venue_id: int = None):
    """Scrape Reddit for venue mentions."""
    scraper = VenueScraper(db)

    if venue_id:
        venue = db.get_venue(venue_id)
        if not venue:
            print(f"Venue ID {venue_id} not found.")
            return

        print(f"Searching Reddit for: {venue['name']}...")
        count = scraper.search_reddit_for_venue(venue['name'], venue_id)
        print(f"Found {count} mentions.")
    else:
        print("Searching Reddit for all venues...")
        venues = db.get_all_venues()

        for venue in venues:
            print(f"\nSearching for: {venue['name']}...")
            count = scraper.search_reddit_for_venue(venue['name'], venue['id'])
            print(f"  Found {count} mentions.")


def search_reviews(db: VenueDatabase, venue_id: int):
    """Search for venue reviews."""
    venue = db.get_venue(venue_id)
    if not venue:
        print(f"Venue ID {venue_id} not found.")
        return

    print(f"Searching for reviews: {venue['name']}...")
    scraper = VenueScraper(db)
    summary = scraper.search_venue_reviews(venue['name'], venue['location'])

    # Update venue with review summary
    db.update_venue(venue_id, review_summary=summary)

    print("\n" + "=" * 100)
    print("Review Summary:")
    print("=" * 100)
    print(summary)
    print()


def export_to_csv(db: VenueDatabase, filename: str = "venues_export.csv"):
    """Export all venues to CSV."""
    venues = db.get_all_venues()

    if not venues:
        print("No venues to export.")
        return

    fieldnames = ['id', 'name', 'location', 'region', 'website', 'capacity',
                 'overnight_accommodations', 'price_range', 'multi_day_available',
                 'notes', 'review_summary']

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for venue in venues:
                row = {k: venue.get(k, '') for k in fieldnames}
                writer.writerow(row)

        print(f"✓ Exported {len(venues)} venues to {filename}")
    except Exception as e:
        print(f"✗ Error exporting to CSV: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Wedding Venue Finder - Research tool for wedding venues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list --region NorCal --capacity 150
  %(prog)s view 1 --reddit
  %(prog)s add
  %(prog)s scrape-reddit --venue-id 1
  %(prog)s search-reviews --venue-id 1
  %(prog)s export venues.csv
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List venues')
    list_parser.add_argument('--region', choices=['NorCal', 'Washington', 'San Juan Islands'],
                           help='Filter by region')
    list_parser.add_argument('--capacity', type=int, help='Minimum capacity')
    list_parser.add_argument('--accommodations', choices=['yes', 'no', 'nearby'],
                           help='Filter by overnight accommodations')

    # View command
    view_parser = subparsers.add_parser('view', help='View venue details')
    view_parser.add_argument('venue_id', type=int, help='Venue ID')
    view_parser.add_argument('--reddit', action='store_true', help='Show Reddit mentions')

    # Add command
    subparsers.add_parser('add', help='Add new venue (interactive)')

    # Scrape Reddit command
    scrape_parser = subparsers.add_parser('scrape-reddit', help='Scrape Reddit for mentions')
    scrape_parser.add_argument('--venue-id', type=int, help='Specific venue ID (optional)')

    # Search reviews command
    review_parser = subparsers.add_parser('search-reviews', help='Search for venue reviews')
    review_parser.add_argument('--venue-id', type=int, required=True, help='Venue ID')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export venues to CSV')
    export_parser.add_argument('filename', nargs='?', default='venues_export.csv',
                             help='Output filename (default: venues_export.csv)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    db = VenueDatabase()

    if args.command == 'list':
        list_venues(db, args.region, args.capacity, args.accommodations)
    elif args.command == 'view':
        view_venue(db, args.venue_id, args.reddit)
    elif args.command == 'add':
        add_venue(db)
    elif args.command == 'scrape-reddit':
        scrape_reddit_mentions(db, args.venue_id)
    elif args.command == 'search-reviews':
        search_reviews(db, args.venue_id)
    elif args.command == 'export':
        export_to_csv(db, args.filename)


if __name__ == "__main__":
    main()
