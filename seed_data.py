"""Seed database with initial wedding venues."""
from database import VenueDatabase


def seed_venues():
    """Populate database with initial venue data."""
    db = VenueDatabase()

    venues = [
        # Northern California
        {
            'name': 'Carmel Valley Ranch',
            'location': 'Carmel Valley, CA',
            'region': 'NorCal',
            'website': 'https://www.carmelvalleyranch.com/',
            'capacity': 200,
            'overnight_accommodations': 'yes',
            'price_range': '$$$$$',
            'multi_day_available': True,
            'notes': 'Luxury resort in scenic Carmel Valley. Multiple event spaces. Golf course on-site.'
        },
        {
            'name': 'Cavallo Point',
            'location': 'Sausalito, CA',
            'region': 'NorCal',
            'website': 'https://www.cavallopoint.com/',
            'capacity': 180,
            'overnight_accommodations': 'yes',
            'price_range': '$$$$$',
            'multi_day_available': True,
            'notes': 'Historic lodge at Golden Gate National Park. Stunning bay and bridge views.'
        },
        {
            'name': 'Holman Ranch',
            'location': 'Carmel Valley, CA',
            'region': 'NorCal',
            'website': 'https://holmanranch.com/',
            'capacity': 175,
            'overnight_accommodations': 'nearby',
            'price_range': '$$$$',
            'multi_day_available': True,
            'notes': 'Working ranch and vineyard. Rustic elegance with mountain views.'
        },
        {
            'name': 'Calistoga Ranch',
            'location': 'Calistoga, CA',
            'region': 'NorCal',
            'website': 'https://www.aubergeresorts.com/calistogaranch/',
            'capacity': 150,
            'overnight_accommodations': 'yes',
            'price_range': '$$$$$',
            'multi_day_available': True,
            'notes': 'Luxury Napa Valley resort. Private lodges, canyon setting.'
        },
        {
            'name': 'The Estate Yountville',
            'location': 'Yountville, CA',
            'region': 'NorCal',
            'website': 'https://www.theestateyountville.com/',
            'capacity': 200,
            'overnight_accommodations': 'yes',
            'price_range': '$$$$$',
            'multi_day_available': True,
            'notes': 'Elegant estate in heart of Napa Valley wine country.'
        },
        {
            'name': 'Costanoa',
            'location': 'Pescadero, CA',
            'region': 'NorCal',
            'website': 'https://www.costanoa.com/',
            'capacity': 150,
            'overnight_accommodations': 'yes',
            'price_range': '$$$',
            'multi_day_available': True,
            'notes': 'Coastal lodge and camp. Ocean views, redwood forests. More casual vibe.'
        },

        # Washington
        {
            'name': 'Suncadia Resort',
            'location': 'Cle Elum, WA',
            'region': 'Washington',
            'website': 'https://www.destinationhotels.com/suncadia-resort',
            'capacity': 200,
            'overnight_accommodations': 'yes',
            'price_range': '$$$$',
            'multi_day_available': True,
            'notes': 'Mountain resort in Cascades. Multiple venues, golf, spa. 90 mins from Seattle.'
        },
        {
            'name': 'Chateau Lill',
            'location': 'Woodinville, WA',
            'region': 'Washington',
            'website': 'https://www.chateaulill.com/',
            'capacity': 150,
            'overnight_accommodations': 'nearby',
            'price_range': '$$$$',
            'multi_day_available': True,
            'notes': 'French-inspired winery estate. 30 mins from Seattle. Beautiful gardens.'
        },
        {
            'name': 'DeLille Cellars',
            'location': 'Woodinville, WA',
            'region': 'Washington',
            'website': 'https://www.delillecellars.com/',
            'capacity': 175,
            'overnight_accommodations': 'nearby',
            'price_range': '$$$$',
            'multi_day_available': False,
            'notes': 'Acclaimed winery with event space. Woodinville wine country.'
        },
        {
            'name': 'Sleeping Lady Mountain Resort',
            'location': 'Leavenworth, WA',
            'region': 'Washington',
            'website': 'https://www.sleepinglady.com/',
            'capacity': 200,
            'overnight_accommodations': 'yes',
            'price_range': '$$$',
            'multi_day_available': True,
            'notes': 'Mountain retreat near Bavarian village. Conference facilities, nature setting.'
        },

        # San Juan Islands
        {
            'name': 'Roche Harbor Resort',
            'location': 'San Juan Island, WA',
            'region': 'San Juan Islands',
            'website': 'https://www.rocheharbor.com/',
            'capacity': 200,
            'overnight_accommodations': 'yes',
            'price_range': '$$$$',
            'multi_day_available': True,
            'notes': 'Historic resort with marina. Multiple venue options. Waterfront setting.'
        },
        {
            'name': 'Rosario Resort & Spa',
            'location': 'Orcas Island, WA',
            'region': 'San Juan Islands',
            'website': 'https://www.rosarioresort.com/',
            'capacity': 175,
            'overnight_accommodations': 'yes',
            'price_range': '$$$$',
            'multi_day_available': True,
            'notes': 'Historic mansion on Cascade Bay. Spa, marina, stunning water views.'
        },
        {
            'name': 'Outlook Inn',
            'location': 'Orcas Island, WA',
            'region': 'San Juan Islands',
            'website': 'https://www.outlookinn.com/',
            'capacity': 120,
            'overnight_accommodations': 'yes',
            'price_range': '$$$',
            'multi_day_available': True,
            'notes': 'Boutique waterfront hotel in Eastsound. Intimate island setting.'
        },
        {
            'name': 'Friday Harbor House',
            'location': 'San Juan Island, WA',
            'region': 'San Juan Islands',
            'website': 'https://www.fridayharborhouse.com/',
            'capacity': 100,
            'overnight_accommodations': 'yes',
            'price_range': '$$$$',
            'multi_day_available': True,
            'notes': 'Boutique waterfront hotel. Smaller capacity, perfect for intimate gatherings.'
        }
    ]

    print("Seeding database with venues...")
    for venue_data in venues:
        try:
            venue_id = db.add_venue(**venue_data)
            print(f"✓ Added: {venue_data['name']} (ID: {venue_id})")
        except Exception as e:
            print(f"✗ Error adding {venue_data['name']}: {e}")

    print(f"\nSeeded {len(venues)} venues successfully!")
    print("\nVenue counts by region:")
    for region in ['NorCal', 'Washington', 'San Juan Islands']:
        venues = db.search_venues(region=region)
        print(f"  {region}: {len(venues)} venues")


if __name__ == "__main__":
    seed_venues()
