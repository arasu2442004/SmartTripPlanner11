"""
Smart Trip Planner - Database Module
SQLite Database Setup, Schema Definitions, and Initial Seed Data
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Path to SQLite database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trip_planner.db')


def get_db_connection():
    """Establish and return a connection to the SQLite database with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and seed sample destinations if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: Users (for optional registration & login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 2: Destinations (Curated Indian destinations with cost metrics)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            state TEXT NOT NULL,
            description TEXT NOT NULL,
            min_days INTEGER NOT NULL,
            transport_cost REAL NOT NULL,
            hotel_per_day REAL NOT NULL,
            food_per_day REAL NOT NULL,
            activity_cost REAL NOT NULL,
            preference TEXT NOT NULL,
            highlights TEXT NOT NULL,
            best_time TEXT DEFAULT 'Year-round',
            image_url TEXT
        )
    ''')

    # Table 3: Trips (User planned/saved itineraries)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            destination_id INTEGER NOT NULL,
            start_location TEXT NOT NULL,
            budget REAL NOT NULL,
            days INTEGER NOT NULL,
            travelers INTEGER NOT NULL,
            preference TEXT NOT NULL,
            total_cost REAL NOT NULL,
            remaining_budget REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (destination_id) REFERENCES destinations (id)
        )
    ''')

    conn.commit()

    # Seed initial destination data if table is currently empty
    cursor.execute('SELECT COUNT(*) FROM destinations')
    if cursor.fetchone()[0] == 0:
        seed_destinations(cursor)
        conn.commit()
        print("Database initialized and 18 destinations seeded successfully.")
    else:
        print("Database already contains destination data.")

    conn.close()


def seed_destinations(cursor):
    """Seed comprehensive 18 Indian travel destinations across different preferences."""
    sample_destinations = [
        (
            "Ooty", "Tamil Nadu",
            "The Queen of Hill Stations featuring lush tea gardens, misty blue Nilgiri mountains, and pleasant colonial charm.",
            3, 1800, 2200, 700, 900, "Nature",
            "Ooty Lake boating, Botanical Gardens, Doddabetta Peak view, Nilgiri Mountain Toy Train, Pykara Waterfalls",
            "October to June",
            "https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Kodaikanal", "Tamil Nadu",
            "Princess of Hill Stations renowned for scenic star-shaped lake, pine forests, and cool misty viewpoints.",
            3, 1900, 2000, 650, 800, "Nature",
            "Kodai Lake pedal boating, Coaker's Walk, Pillar Rocks panoramic view, Bryant Park, Pine Forest stroll",
            "September to May",
            "https://images.unsplash.com/photo-1627916607164-7b20241db935?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Munnar", "Kerala",
            "Idyllic green tea hills, rolling mist, cascading waterfalls, and spice plantations in God's Own Country.",
            3, 2200, 2400, 750, 1000, "Nature",
            "Tea Museum tour, Mattupetty Dam, Eravikulam National Park (Nilgiri Tahr), Top Station viewpoint, Echo Point",
            "September to March",
            "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Coorg", "Karnataka",
            "The Scotland of India surrounded by fragrant coffee estates, lush misty hills, and rich Kodava culture.",
            2, 1700, 2500, 800, 950, "Nature",
            "Abbey Falls, Raja's Seat sunset, Dubare Elephant Camp, Talakaveri source of river Kaveri, Coffee tasting",
            "October to April",
            "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Goa", "Goa",
            "Tropical paradise with sun-kissed golden sand beaches, Portuguese heritage churches, and vibrant seaside nightlife.",
            4, 2500, 2800, 1100, 1500, "Beach",
            "Baga Beach watersports, Fort Aguada, Basilica of Bom Jesus, Anjuna Flea Market, Mandovi sunset cruise",
            "November to February",
            "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Mysore", "Karnataka",
            "The City of Palaces celebrated for opulent royal heritage, silk weaving, sandalwood, and grand Dasara architecture.",
            2, 1200, 1800, 600, 700, "Historical",
            "Mysore Palace illumination, Chamundi Hill Temple, Brindavan Gardens fountain show, St. Philomena's Cathedral",
            "October to March",
            "https://images.unsplash.com/photo-1600100397608-f010f443b749?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Pondicherry", "Puducherry",
            "Charming French colonial seaside town with cobblestone boulevards, pastel villas, and serene spiritual aura.",
            3, 1600, 2400, 900, 850, "Beach",
            "Promenade Beach sunrise walk, French Quarter heritage tour, Auroville Matrimandir, Paradise Beach ferry",
            "October to March",
            "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Wayanad", "Kerala",
            "Picturesque highland paradise featuring prehistoric caves, tranquil waterfalls, spice trails, and treehouses.",
            3, 2000, 2200, 700, 1100, "Adventure",
            "Edakkal prehistoric cave hike, Banasura Sagar Earth Dam, Chembra Peak heart-shaped lake, Soochipara Falls",
            "October to May",
            "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Jaipur", "Rajasthan",
            "The Pink City boasting majestic sandstone fortresses, colorful royal bazaars, and opulent Rajasthani palaces.",
            3, 2200, 2600, 850, 1200, "Historical",
            "Amer Fort elephant viewpoint, Hawa Mahal photo-stop, City Palace museum, Jantar Mantar observatory, Chokhi Dhani",
            "October to March",
            "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Manali", "Himachal Pradesh",
            "Snow-capped Himalayan wonderland packed with adventure sports, pine valleys, and refreshing mountain streams.",
            4, 3000, 2500, 850, 2000, "Adventure",
            "Solang Valley paragliding & zorbing, Atal Tunnel drive, Hadimba Wooden Temple, Old Manali hipster cafes, Jogini Falls",
            "October to June",
            "https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Rishikesh", "Uttarakhand",
            "The Yoga Capital of the World on the holy Ganges offering adrenaline-pumping river rafting and tranquil spiritual vibes.",
            3, 2400, 2000, 650, 1800, "Adventure",
            "Ganges White Water Rafting, Bungee jumping at Mohan Chatti, Triveni Ghat evening Maha Aarti, Lakshman Jhula walk",
            "September to May",
            "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Varanasi", "Uttar Pradesh",
            "The spiritual heart of India and one of the world's oldest living cities along the revered banks of river Ganga.",
            3, 2100, 1900, 550, 750, "Religious",
            "Sunrise Ganges boat cruise, Dashashwamedh Ghat evening Ganga Aarti, Kashi Vishwanath temple darshan, Sarnath stupa",
            "October to March",
            "https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Hyderabad", "Telangana",
            "The City of Pearls blending legendary Nizami architecture, world-famous biryani culinary culture, and tech grandeur.",
            2, 1500, 2300, 750, 800, "Historical",
            "Charminar & Laad Bazaar, Golconda Fort sound & light show, Salar Jung Museum, Hussain Sagar Buddha statue boat ride",
            "October to March",
            "https://images.unsplash.com/photo-1605335198160-6395dc48b5ff?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Bengaluru", "Karnataka",
            "The vibrant Garden City and Silicon Valley of India famous for pleasant weather, expansive parks, and craft breweries.",
            2, 1400, 2500, 950, 850, "Historical",
            "Lalbagh Botanical Garden glass house, Bangalore Palace, Cubbon Park stroll, Bannerghatta National Park safari",
            "Year-round",
            "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Alleppey", "Kerala",
            "The Venice of the East celebrated for serene emerald backwaters, traditional thatched houseboats, and village lagoons.",
            3, 2300, 3200, 850, 1200, "Nature",
            "Overnight Houseboat backwater cruise, Marari Beach sunset, Kayaking in narrow canals, Kuttanad paddy fields",
            "October to March",
            "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Udaipur", "Rajasthan",
            "The City of Lakes featuring romantic marble palaces, shimmering Lake Pichola, and fairytale sunsets.",
            3, 2400, 2700, 900, 1100, "Historical",
            "Lake Pichola boat cruise to Jag Mandir, City Palace complex, Saheliyon-ki-Bari, Bagore Ki Haveli folk dance show",
            "September to March",
            "https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Darjeeling", "West Bengal",
            "Queen of the Hills offering dramatic views of Mount Kanchenjunga, world-class aromatic tea estates, and heritage toy train.",
            4, 2800, 2300, 750, 1000, "Nature",
            "Tiger Hill Kanchenjunga sunrise, Batasia Loop Toy Train ride, Happy Valley Tea Estate, Himalayan Mountaineering Institute",
            "October to May",
            "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=800&auto=format&fit=crop&q=80"
        ),
        (
            "Hampi", "Karnataka",
            "UNESCO World Heritage open-air museum filled with surreal boulder-strewn landscapes and magnificent Vijayanagara ruins.",
            3, 1600, 1900, 600, 800, "Historical",
            "Virupaksha Temple, Stone Chariot at Vijaya Vittala temple, Coracle boat ride on Tungabhadra, Matanga Hill sunrise",
            "October to March",
            "https://images.unsplash.com/photo-1600100397608-f010f443b749?w=800&auto=format&fit=crop&q=80"
        )
    ]

    cursor.executemany('''
        INSERT INTO destinations (
            name, state, description, min_days, transport_cost,
            hotel_per_day, food_per_day, activity_cost, preference,
            highlights, best_time, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_destinations)


# Database CRUD Operations Helper Functions

def get_all_destinations():
    """Retrieve all destination records."""
    conn = get_db_connection()
    destinations = conn.execute('SELECT * FROM destinations ORDER BY name ASC').fetchall()
    conn.close()
    return destinations


def get_destination_by_id(destination_id):
    """Retrieve a single destination by its ID."""
    conn = get_db_connection()
    destination = conn.execute('SELECT * FROM destinations WHERE id = ?', (destination_id,)).fetchone()
    conn.close()
    return destination


def create_user(name, email, password):
    """Register a new user with hashed password. Returns user id or None if email exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            (name, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def authenticate_user(email, password):
    """Verify user credentials. Returns user row if valid, otherwise None."""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        return user
    return None


def get_user_by_id(user_id):
    """Fetch user by id."""
    conn = get_db_connection()
    user = conn.execute('SELECT id, name, email, created_at FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user


def save_user_trip(user_id, destination_id, start_location, budget, days, travelers, preference, total_cost, remaining_budget):
    """Save planned trip to trips table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trips (
            user_id, destination_id, start_location, budget, days,
            travelers, preference, total_cost, remaining_budget
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, destination_id, start_location, budget, days, travelers, preference, total_cost, remaining_budget))
    conn.commit()
    trip_id = cursor.lastrowid
    conn.close()
    return trip_id


def get_user_trips(user_id):
    """Retrieve all trips saved by a specific user with destination details."""
    conn = get_db_connection()
    trips = conn.execute('''
        SELECT t.*, d.name as destination_name, d.state as destination_state, 
               d.image_url as destination_image, d.highlights as destination_highlights
        FROM trips t
        JOIN destinations d ON t.destination_id = d.id
        WHERE t.user_id = ?
        ORDER BY t.created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return trips


def delete_user_trip(trip_id, user_id):
    """Delete a trip belonging to a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trips WHERE id = ? AND user_id = ?', (trip_id, user_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


if __name__ == '__main__':
    # Initialize DB when run directly
    init_db()
