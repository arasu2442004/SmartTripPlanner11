# Smart Trip Planner 🌍✈️
> **A Budget & Duration-Driven Travel Recommendation and Itinerary Generation Web Application**
> Built with **Python (Flask)**, **SQLite**, **HTML5**, **Vanilla CSS3**, and **JavaScript**.

---

## 📌 1. Project Overview & Abstract

Planning a trip often leads to frustration when travelers encounter complex search engines that force them to pick a destination before knowing whether it fits their wallet or schedule. 

**Smart Trip Planner** solves this by flipping the planning paradigm:
1. The user inputs their **starting city**, **trip budget in ₹**, **number of days**, **number of travelers**, and **travel preference** (e.g., Nature, Beach, Adventure, Historical, Religious).
2. The application's transparent **Recommendation Algorithm** scores and selects the **Top 3 most suitable destinations**.
3. For each recommended spot, the system generates:
   - A **Suitability Match Score** (0–100%)
   - A clear explanation of **"Why this destination is suitable"**
   - An **itemized cost breakdown** (Transportation, Hotels, Meals, Sightseeing, Buffer)
   - A dynamic **Day-by-Day Itinerary** with morning, afternoon, and evening schedules.
4. Users can register/login to **Save Trips** to their personal dashboard, print/export the plans to PDF, or manage previous trips.

---

## 🏗️ 2. Technology Stack

| Layer | Technology | Rationale / Benefits |
|---|---|---|
| **Frontend** | HTML5, Modern Vanilla CSS3, Vanilla JavaScript | Zero build step or heavy node dependencies; instant loading, full responsiveness, and smooth glassmorphism styling. |
| **Backend** | Python 3.12, Flask 3.0+ | Lightweight, beginner-friendly yet robust WSGI framework; ideal for academic demonstrations. |
| **Database** | SQLite3 | Serverless, zero-configuration SQL database embedded directly in the project directory (`trip_planner.db`). |
| **Security** | Werkzeug Security | Secure one-way password hashing using `generate_password_hash` (PBKDF2/scrypt). |
| **Design System** | Custom CSS + Google Fonts | Typography via *Outfit* and *Plus Jakarta Sans*; accessible contrast and mobile-first responsive layout. |

---

## 📁 3. Project Directory Structure

```text
smart-trip-planner/
│
├── app.py                      # Flask routes, sessions, request handling, and error views
├── database.py                 # SQLite initialization, schema creation, seed data (18 Indian destinations)
├── recommendation.py           # Transparent scoring algorithm, cost estimation & itinerary generator
├── test_app.py                 # Automated unit and integration test suite
├── requirements.txt            # Python dependencies (Flask, Werkzeug)
├── README.md                   # Comprehensive project documentation & Viva guide
├── trip_planner.db             # SQLite database file (created automatically on startup)
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern custom CSS (glassmorphism, badges, budget meters, print styles)
│   └── js/
│       └── main.js             # Client-side steppers, budget chips, print trigger, mobile toggle
│
└── templates/
    ├── base.html               # Shared layout: sticky navbar, alerts, footer
    ├── index.html              # Homepage with hero section, statistics, 4-step workflow, and features
    ├── plan.html               # Trip input form with rupee presets and preference cards
    ├── recommendations.html    # Top 3 suggested destination cards with suitability explanations
    ├── trip_details.html       # Day-by-day itinerary schedule and itemized budget breakdown
    ├── destinations.html       # Catalog of all 18 destinations with theme filters
    ├── my_trips.html           # User dashboard for viewing and deleting saved trip plans
    ├── login.html              # User login interface
    ├── register.html           # New user registration interface
    ├── 404.html                # Custom Not Found error page
    └── 500.html                # Custom Server Error page
```

---

## 🧮 4. Recommendation Scoring Algorithm

Instead of an opaque or unpredictable black-box ML model, Smart Trip Planner employs a **deterministic, rule-based multi-criteria scoring algorithm** that is explainable and defensible during viva evaluations.

### Step 1: Estimated Total Trip Cost Calculation
Let:
- $N$ = Number of travelers
- $D$ = Trip duration in days
- $\text{Rooms} = \lceil N / 2 \rceil$ (assumes 2 people per room)
- $C_{trans}$ = Transportation cost per person
- $C_{hotel}$ = Average hotel room cost per night
- $C_{food}$ = Average food cost per person per day
- $C_{act}$ = Sightseeing & activity entry cost per person

$$\text{Total Cost } (C_{total}) = (C_{trans} \times N) + (C_{hotel} \times \text{Rooms} \times D) + (C_{food} \times N \times D) + (C_{act} \times N) + C_{misc}$$

Where $C_{misc} = 5\% \times (C_{hotel} + C_{food} + C_{act})$ provides an authentic buffer for auto-rickshaws, local snacks, and tips.

---

### Step 2: Component Scoring (Max 100 Points)

$$\text{Suitability Score} = \text{Budget Score } (40\%) + \text{Days Score } (30\%) + \text{Preference Score } (30\%)$$

#### 1. Budget Match Score (Max 40 Points)
- **Within Budget ($C_{total} \le \text{Budget}$)**:
  - If utilization is between $70\%$ and $98\% \rightarrow \mathbf{40 \text{ pts}}$ (optimal budget match).
  - If utilization is between $50\%$ and $70\% \rightarrow \mathbf{35 \text{ pts}}$ (comfortable buffer).
  - If utilization is $< 50\% \rightarrow \mathbf{30 \text{ pts}}$ (economical, large surplus).
- **Over Budget ($C_{total} > \text{Budget}$)**:
  - Over by $\le 10\% \rightarrow \mathbf{22 \text{ pts}}$ (minor stretch).
  - Over by $10\% - 25\% \rightarrow \mathbf{12 \text{ pts}}$.
  - Over by $> 25\% \rightarrow \mathbf{4 \text{ pts}}$.

#### 2. Days Match Score (Max 30 Points)
- Compares user requested days ($D$) with destination's recommended minimum duration ($D_{min}$):
  - $D = D_{min} \rightarrow \mathbf{30 \text{ pts}}$ (perfect pacing).
  - $D = D_{min} + 1 \rightarrow \mathbf{28 \text{ pts}}$ (relaxed, comfortable exploration).
  - $D > D_{min} + 1 \rightarrow \mathbf{24 \text{ pts}}$ (extended leisure).
  - $D < D_{min} \rightarrow \mathbf{16 \text{ pts}}$ (1 day short) or $\mathbf{8 \text{ pts}}$ (severely rushed).

#### 3. Preference Match Score (Max 30 Points)
- **Exact Match**: User preference matches destination primary category $\rightarrow \mathbf{30 \text{ pts}}$.
- **Complementary Match**: Related themes (e.g. Nature & Adventure, or Historical & Religious) $\rightarrow \mathbf{18 \text{ pts}}$.
- **Alternative Theme**: $\rightarrow \mathbf{10 \text{ pts}}$.

Destinations are sorted by $\text{Suitability Score}$ descending, and the top 3 are rendered to the user.

---

## 🗄️ 5. Database Schema & Tables

### Table 1: `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| `name` | TEXT | NOT NULL | User's full name |
| `email` | TEXT | UNIQUE NOT NULL | User's login email |
| `password` | TEXT | NOT NULL | Hashed password string |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

### Table 2: `destinations`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique destination ID |
| `name` | TEXT | NOT NULL | City / destination name (e.g. Ooty, Goa, Munnar) |
| `state` | TEXT | NOT NULL | Indian state (e.g. Tamil Nadu, Kerala, Goa) |
| `description` | TEXT | NOT NULL | Engaging destination summary |
| `min_days` | INTEGER | NOT NULL | Minimum recommended duration in days |
| `transport_cost`| REAL | NOT NULL | Average one-way/transit cost per traveler |
| `hotel_per_day` | REAL | NOT NULL | Average hotel tariff per room per night |
| `food_per_day` | REAL | NOT NULL | Daily food allowance per traveler |
| `activity_cost`| REAL | NOT NULL | Sightseeing and activity fees per traveler |
| `preference` | TEXT | NOT NULL | Theme: Nature, Beach, Adventure, Historical, Religious |
| `highlights` | TEXT | NOT NULL | Comma-separated list of top attractions |
| `best_time` | TEXT | DEFAULT 'Year-round' | Ideal travel months |
| `image_url` | TEXT | NULLABLE | High-resolution photography URL |

### Table 3: `trips`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique trip itinerary ID |
| `user_id` | INTEGER | FOREIGN KEY REFERENCES users(id) | Associated user account |
| `destination_id`| INTEGER| FOREIGN KEY REFERENCES destinations(id) | Destination selected |
| `start_location`| TEXT | NOT NULL | Starting city (e.g., Chennai, Bangalore) |
| `budget` | REAL | NOT NULL | User allocated budget in ₹ |
| `days` | INTEGER | NOT NULL | Selected trip duration |
| `travelers` | INTEGER | NOT NULL | Number of travelers |
| `preference` | TEXT | NOT NULL | Selected travel theme |
| `total_cost` | REAL | NOT NULL | Calculated estimated total cost |
| `remaining_budget`| REAL | NOT NULL | Budget minus total cost |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Trip save timestamp |

---

## 🚀 6. Step-by-Step Local Setup & Execution Guide

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your computer.
- A modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox).

### 1. Clone / Navigate to the Project Directory
```bash
cd smart-trip-planner
```

### 2. (Optional but Recommended) Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database & Seed 18 Indian Destinations
```bash
python database.py
```
*(The SQLite database `trip_planner.db` will be created automatically and pre-seeded with 18 destinations).*

### 5. Run the Automated Tests (Verification)
```bash
python test_app.py
```
*Expected Output:*
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.214s

OK
[PASS] Test 1: 18 destinations verified in database.
[PASS] Test 2: Top recommendations Munnar (100.0%), Alleppey (100.0%), Coorg (98.0%)
[PASS] Test 3: Dynamic itinerary generation verified for 3 and 5 days.
[PASS] Test 4: Home and Plan pages rendered successfully.
[PASS] Test 5: POST /recommend generates top 3 suggestions.
[PASS] Test 6: Trip details and itemized budget breakdown verified.
[PASS] Test 7: User registration, trip save, dashboard, and logout verified.
```

### 6. Run the Application Server
```bash
python app.py
```

### 7. Open the App in Your Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🎓 7. Viva & Project Evaluation Q&A (For Final-Year Defense)

### Q1: What problem does this application solve?
> **Answer**: Most travel websites require users to search by destination first, which leads to budget overruns or mismatched schedules. Smart Trip Planner reverses the flow: users enter their constraints (starting city, ₹ budget, duration, and theme), and the system recommends the most cost-effective and duration-appropriate destinations.

### Q2: Why did you choose a rule-based algorithm over Machine Learning?
> **Answer**: For a college trip recommendation system, transparency, explainability, and determinism are paramount. ML models require large user interaction datasets (cold-start problem) and often act as "black boxes." Our mathematical multi-criteria scoring algorithm provides clear weights (40% Budget, 30% Duration, 30% Preference) that are 100% explainable to the user through the "Why this destination is suitable" feature.

### Q3: How do you handle room allocation for odd numbers of travelers?
> **Answer**: We use the ceiling function: $\text{Rooms} = \lceil \text{Travelers} / 2 \rceil$. For instance, 3 travelers require $\lceil 3/2 \rceil = 2$ rooms, preventing under-estimation of accommodation expenses.

### Q4: How is user security managed?
> **Answer**: Passwords are never stored in plain text. We utilize Werkzeug's `generate_password_hash()` and `check_password_hash()` which implement industry-standard cryptographic salting and key stretching. Sessions are signed using Flask's secret key.

### Q5: Can users plan trips without creating an account?
> **Answer**: Yes! The application supports guest planning mode, allowing anyone to enter parameters, inspect recommendations, view the day-by-day plan, and review the budget breakdown immediately. An account is only required when the user chooses to "Save Trip" to their persistent dashboard.

---

## 💼 8. Resume Bullet Points (Copy & Paste for Software / ECE Roles)

- **Smart Trip Planner (Full-Stack Python/Flask Web Application)**:
  - *Architected a full-stack algorithmic travel planner using Python, Flask, SQLite, and vanilla responsive CSS/JS to recommend optimal Indian travel destinations based on user budget, duration, and preferences.*
  - *Engineered a deterministic multi-criteria recommendation algorithm integrating budget utilization, day pace, and travel theme affinities to score and rank destinations with 100% explainability.*
  - *Developed dynamic day-by-day itinerary synthesis and itemized cost breakdown algorithms calculating transportation, lodging, meals, and contingency reserves for multiple travelers.*
  - *Implemented secure user authentication with password hashing (Werkzeug), session state persistence, and an interactive dashboard for managing saved itineraries.*
  - *Created comprehensive unit and integration test suites using Python's `unittest` framework achieving 100% route and model verification.*
