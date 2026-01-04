"""Database management for wedding venue finder."""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class VenueDatabase:
    """Manages database for wedding venues (SQLite or PostgreSQL)."""

    def __init__(self, db_path: str = "data/venues.db"):
        # Check if we should use PostgreSQL (for Render) or SQLite (for local)
        self.database_url = os.environ.get('DATABASE_URL')

        if self.database_url:
            # Use PostgreSQL
            import psycopg2
            import psycopg2.extras
            self.db_type = 'postgresql'
            self.conn_module = psycopg2
            self.placeholder = '%s'
        else:
            # Use SQLite
            import sqlite3
            self.db_type = 'sqlite'
            self.db_path = db_path
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.conn_module = sqlite3
            self.placeholder = '?'

        self.init_database()

    def get_connection(self):
        """Get database connection."""
        if self.db_type == 'postgresql':
            import psycopg2.extras
            conn = self.conn_module.connect(self.database_url)
            return conn
        else:
            conn = self.conn_module.connect(self.db_path)
            conn.row_factory = self.conn_module.Row
            return conn

    def _dict_from_row(self, row):
        """Convert row to dictionary."""
        if self.db_type == 'postgresql':
            return dict(row)
        else:
            return dict(row)

    def init_database(self):
        """Initialize database with schema."""
        conn = self.get_connection()

        if self.db_type == 'postgresql':
            cursor = conn.cursor()
        else:
            cursor = conn.cursor()

        # Create venues table
        if self.db_type == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS venues (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    region TEXT NOT NULL CHECK(region IN ('NorCal', 'Washington', 'San Juan Islands')),
                    website TEXT,
                    capacity INTEGER,
                    overnight_accommodations TEXT CHECK(overnight_accommodations IN ('yes', 'no', 'nearby')),
                    price_range TEXT,
                    multi_day_available BOOLEAN,
                    notes TEXT,
                    review_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS venues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    region TEXT NOT NULL CHECK(region IN ('NorCal', 'Washington', 'San Juan Islands')),
                    website TEXT,
                    capacity INTEGER,
                    overnight_accommodations TEXT CHECK(overnight_accommodations IN ('yes', 'no', 'nearby')),
                    price_range TEXT,
                    multi_day_available BOOLEAN,
                    notes TEXT,
                    review_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # Create reddit_mentions table
        if self.db_type == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reddit_mentions (
                    id SERIAL PRIMARY KEY,
                    venue_id INTEGER NOT NULL,
                    thread_title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    key_quotes TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (venue_id) REFERENCES venues (id) ON DELETE CASCADE
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reddit_mentions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venue_id INTEGER NOT NULL,
                    thread_title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    key_quotes TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (venue_id) REFERENCES venues (id) ON DELETE CASCADE
                )
            """)

        # Create search_cache table for rate limiting
        if self.db_type == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    id SERIAL PRIMARY KEY,
                    query TEXT NOT NULL UNIQUE,
                    results TEXT NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL UNIQUE,
                    results TEXT NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        conn.commit()
        conn.close()

    def add_venue(self, name: str, location: str, region: str, **kwargs) -> int:
        """Add a new venue to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()

        fields = ['name', 'location', 'region']
        values = [name, location, region]

        optional_fields = ['website', 'capacity', 'overnight_accommodations',
                          'price_range', 'multi_day_available', 'notes', 'review_summary']

        for field in optional_fields:
            if field in kwargs and kwargs[field] is not None:
                fields.append(field)
                values.append(kwargs[field])

        placeholders = ','.join([self.placeholder for _ in values])
        field_names = ','.join(fields)

        if self.db_type == 'postgresql':
            cursor.execute(
                f"INSERT INTO venues ({field_names}) VALUES ({placeholders}) RETURNING id",
                values
            )
            venue_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                f"INSERT INTO venues ({field_names}) VALUES ({placeholders})",
                values
            )
            venue_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return venue_id

    def update_venue(self, venue_id: int, **kwargs):
        """Update venue information."""
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['name', 'location', 'region', 'website', 'capacity',
                         'overnight_accommodations', 'price_range', 'multi_day_available',
                         'notes', 'review_summary']

        updates = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = {self.placeholder}")
                values.append(value)

        if not updates:
            conn.close()
            return

        values.append(venue_id)
        cursor.execute(
            f"UPDATE venues SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = {self.placeholder}",
            values
        )

        conn.commit()
        conn.close()

    def get_venue(self, venue_id: int) -> Optional[Dict[str, Any]]:
        """Get a single venue by ID."""
        conn = self.get_connection()

        if self.db_type == 'postgresql':
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM venues WHERE id = {self.placeholder}", (venue_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def search_venues(self, region: Optional[str] = None,
                     min_capacity: Optional[int] = None,
                     accommodations: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search venues with filters."""
        conn = self.get_connection()

        if self.db_type == 'postgresql':
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = conn.cursor()

        query = "SELECT * FROM venues WHERE 1=1"
        params = []

        if region:
            query += f" AND region = {self.placeholder}"
            params.append(region)

        if min_capacity:
            query += f" AND capacity >= {self.placeholder}"
            params.append(min_capacity)

        if accommodations:
            query += f" AND overnight_accommodations = {self.placeholder}"
            params.append(accommodations)

        query += " ORDER BY name"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_all_venues(self) -> List[Dict[str, Any]]:
        """Get all venues."""
        conn = self.get_connection()

        if self.db_type == 'postgresql':
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = conn.cursor()

        cursor.execute("SELECT * FROM venues ORDER BY region, name")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def add_reddit_mention(self, venue_id: int, thread_title: str,
                          url: str, key_quotes: Optional[str] = None):
        """Add a Reddit mention for a venue."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"INSERT INTO reddit_mentions (venue_id, thread_title, url, key_quotes) VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})",
            (venue_id, thread_title, url, key_quotes)
        )

        conn.commit()
        conn.close()

    def get_reddit_mentions(self, venue_id: int) -> List[Dict[str, Any]]:
        """Get Reddit mentions for a venue."""
        conn = self.get_connection()

        if self.db_type == 'postgresql':
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = conn.cursor()

        cursor.execute(
            f"SELECT * FROM reddit_mentions WHERE venue_id = {self.placeholder} ORDER BY scraped_at DESC",
            (venue_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def cache_search(self, query: str, results: Any):
        """Cache search results."""
        conn = self.get_connection()
        cursor = conn.cursor()

        results_json = json.dumps(results)

        if self.db_type == 'postgresql':
            # PostgreSQL: Use ON CONFLICT for upsert
            cursor.execute(
                f"INSERT INTO search_cache (query, results, cached_at) VALUES ({self.placeholder}, {self.placeholder}, CURRENT_TIMESTAMP) ON CONFLICT (query) DO UPDATE SET results = EXCLUDED.results, cached_at = CURRENT_TIMESTAMP",
                (query, results_json)
            )
        else:
            # SQLite: Use INSERT OR REPLACE
            cursor.execute(
                f"INSERT OR REPLACE INTO search_cache (query, results, cached_at) VALUES ({self.placeholder}, {self.placeholder}, CURRENT_TIMESTAMP)",
                (query, results_json)
            )

        conn.commit()
        conn.close()

    def get_cached_search(self, query: str, max_age_hours: int = 24) -> Optional[Any]:
        """Get cached search results if not too old."""
        conn = self.get_connection()

        if self.db_type == 'postgresql':
            import psycopg2.extras
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cursor = conn.cursor()

        if self.db_type == 'postgresql':
            # PostgreSQL: Use interval for date arithmetic
            cursor.execute(
                f"""SELECT results FROM search_cache
                   WHERE query = {self.placeholder}
                   AND cached_at > NOW() - INTERVAL '{max_age_hours} hours'""",
                (query,)
            )
        else:
            # SQLite: Use datetime function
            cursor.execute(
                f"""SELECT results FROM search_cache
                   WHERE query = {self.placeholder}
                   AND datetime(cached_at, '+{max_age_hours} hours') > datetime('now')""",
                (query,)
            )

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row['results'])
        return None

    def delete_venue(self, venue_id: int):
        """Delete a venue and its mentions."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM venues WHERE id = {self.placeholder}", (venue_id,))

        conn.commit()
        conn.close()
