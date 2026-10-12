"""
Smart Trip Planner - Flask Application
Full-Stack Web Application for Smart Budget-Based Travel Recommendation & Itinerary Planning
"""

import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from database import (
    init_db, get_all_destinations, get_destination_by_id,
    create_user, authenticate_user, get_user_by_id,
    save_user_trip, get_user_trips, delete_user_trip
)
from recommendation import (
    calculate_trip_cost, calculate_suitability,
    get_top_recommendations, generate_itinerary
)

app = Flask(__name__)
# Secret key for session management and flash alerts
app.secret_key = os.environ.get('SECRET_KEY', 'smart-trip-planner-college-proj-secret-key-2026')


# Context processor to make current user info available in all Jinja templates
@app.context_processor
def inject_user():
    return {
        'current_user': {
            'is_authenticated': 'user_id' in session,
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email')
        }
    }


# Route 1: Home Page
@app.route('/')
def index():
    """
    Landing page showcasing project overview, key value props,
    sample popular destinations, and immediate 'Plan My Trip' CTA.
    """
    all_destinations = get_all_destinations()
    # Featured 4 diverse destinations for the homepage showcase
    featured = all_destinations[:4] if len(all_destinations) >= 4 else all_destinations
    return render_template('index.html', featured=featured)


# Route 2: Trip Input Page
@app.route('/plan', methods=['GET'])
def plan():
    """
    Renders the trip planning form where user enters starting city,
    budget in rupees, duration in days, travelers count, and travel preference.
    """
    # Pre-populate defaults or previous session values if available
    defaults = {
        'start_location': session.get('last_start_location', 'Chennai'),
        'budget': session.get('last_budget', 20000),
        'days': session.get('last_days', 3),
        'travelers': session.get('last_travelers', 2),
        'preference': session.get('last_preference', 'Nature')
    }
    return render_template('plan.html', defaults=defaults)


# Route 3: Destination Recommendations Page
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    """
    Receives user trip constraints, runs the recommendation scoring algorithm,
    and displays the top 3 best matching destinations with cost & score breakdowns.
    """
    if request.method == 'POST':
        start_location = request.form.get('start_location', 'Bangalore').strip()
        try:
            budget = float(request.form.get('budget', 25000))
            days = int(request.form.get('days', 3))
            travelers = int(request.form.get('travelers', 2))
        except (ValueError, TypeError):
            flash('Please enter valid numeric values for Budget, Days, and Travelers.', 'warning')
            return redirect(url_for('plan'))

        preference = request.form.get('preference', 'Nature').strip()

        # Cache inputs in session for smooth navigation back and forth
        session['last_start_location'] = start_location
        session['last_budget'] = budget
        session['last_days'] = days
        session['last_travelers'] = travelers
        session['last_preference'] = preference
    else:
        # GET request: Read from query params or session fallback
        start_location = request.args.get('start_location', session.get('last_start_location', 'Bangalore'))
        try:
            budget = float(request.args.get('budget', session.get('last_budget', 25000)))
            days = int(request.args.get('days', session.get('last_days', 3)))
            travelers = int(request.args.get('travelers', session.get('last_travelers', 2)))
        except (ValueError, TypeError):
            budget = 25000.0
            days = 3
            travelers = 2
        preference = request.args.get('preference', session.get('last_preference', 'Nature'))

    # Validate logical inputs
    if budget < 2000:
        flash('Budget should be at least ₹2,000 for a realistic trip calculation.', 'info')
        budget = 2000.0
    if days < 1:
        days = 1
    if travelers < 1:
        travelers = 1

    destinations = get_all_destinations()
    if not destinations:
        init_db()
        destinations = get_all_destinations()

    # Run recommendation algorithm
    top_recommendations = get_top_recommendations(
        destinations=destinations,
        budget=budget,
        days=days,
        travelers=travelers,
        preference=preference,
        limit=3
    )

    query_params = {
        'start_location': start_location,
        'budget': budget,
        'days': days,
        'travelers': travelers,
        'preference': preference
    }

    return render_template(
        'recommendations.html',
        recommendations=top_recommendations,
        params=query_params
    )


# Route 4: Trip Plan & Day-by-Day Itinerary Details Page
@app.route('/trip/<int:destination_id>')
def trip_details(destination_id):
    """
    Renders the selected destination's full details:
    - Day-by-day dynamic itinerary (Morning, Afternoon, Evening)
    - Itemized budget breakdown (Transportation, Hotel, Food, Activities, Misc)
    - Total Estimated Cost & Remaining Budget
    - Save Trip functionality
    """
    destination = get_destination_by_id(destination_id)
    if not destination:
        flash('Selected destination could not be found.', 'danger')
        return redirect(url_for('recommend'))

    # Retrieve current trip parameters from query params or session
    start_location = request.args.get('start_location', session.get('last_start_location', 'Bangalore'))
    try:
        budget = float(request.args.get('budget', session.get('last_budget', 25000)))
        days = int(request.args.get('days', session.get('last_days', destination['min_days'])))
        travelers = int(request.args.get('travelers', session.get('last_travelers', 2)))
    except (ValueError, TypeError):
        budget = 25000.0
        days = destination['min_days']
        travelers = 2

    preference = request.args.get('preference', session.get('last_preference', destination['preference']))

    # Compute itemized costs
    cost_data = calculate_trip_cost(destination, days, travelers)
    remaining_budget = budget - cost_data['total_cost']

    # Compute suitability scores for transparency display
    suitability = calculate_suitability(destination, budget, days, travelers, preference)

    # Generate custom day-by-day plan
    itinerary = generate_itinerary(destination, days, start_location)

    trip_params = {
        'start_location': start_location,
        'budget': budget,
        'days': days,
        'travelers': travelers,
        'preference': preference
    }

    return render_template(
        'trip_details.html',
        destination=destination,
        cost=cost_data,
        remaining_budget=remaining_budget,
        suitability=suitability,
        itinerary=itinerary,
        params=trip_params
    )


# Route 5: Save Trip
@app.route('/save-trip', methods=['POST'])
def save_trip():
    """
    Saves the generated trip plan to the user's account in SQLite.
    If the user is not currently logged in, redirects to login/registration with a notice.
    """
    if 'user_id' not in session:
        flash('Please log in or create a free account to save your trip itinerary.', 'info')
        # Store pending save action in session
        session['pending_save'] = request.form.to_dict()
        return redirect(url_for('login'))

    destination_id = int(request.form.get('destination_id'))
    start_location = request.form.get('start_location', 'City')
    budget = float(request.form.get('budget', 0))
    days = int(request.form.get('days', 1))
    travelers = int(request.form.get('travelers', 1))
    preference = request.form.get('preference', 'General')
    total_cost = float(request.form.get('total_cost', 0))
    remaining_budget = float(request.form.get('remaining_budget', 0))

    user_id = session['user_id']

    trip_id = save_user_trip(
        user_id=user_id,
        destination_id=destination_id,
        start_location=start_location,
        budget=budget,
        days=days,
        travelers=travelers,
        preference=preference,
        total_cost=total_cost,
        remaining_budget=remaining_budget
    )

    if trip_id:
        flash('Trip successfully saved to your dashboard!', 'success')
    else:
        flash('Unable to save trip at this time. Please try again.', 'danger')

    return redirect(url_for('my_trips'))


# Route 6: User Dashboard (My Trips & Saved Trips)
@app.route('/my-trips')
def my_trips():
    """
    Dashboard displaying the user's saved trips and itineraries.
    """
    if 'user_id' not in session:
        flash('Please log in to access your saved trips dashboard.', 'info')
        return redirect(url_for('login'))

    user_id = session['user_id']
    trips = get_user_trips(user_id)
    return render_template('my_trips.html', trips=trips)


# Route 7: Delete Saved Trip
@app.route('/trip/delete/<int:trip_id>', methods=['POST'])
def delete_trip(trip_id):
    """
    Removes a saved trip from the user's dashboard.
    """
    if 'user_id' not in session:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('login'))

    success = delete_user_trip(trip_id, session['user_id'])
    if success:
        flash('Trip removed from your dashboard.', 'info')
    else:
        flash('Failed to remove trip or trip not found.', 'warning')

    return redirect(url_for('my_trips'))


# Route 8: Explore All Destinations
@app.route('/destinations')
def destinations_catalog():
    """
    Shows all curated Indian destinations with filters by preference.
    """
    preference_filter = request.args.get('preference', '').strip()
    all_dests = get_all_destinations()
    
    if preference_filter:
        filtered = [d for d in all_dests if d['preference'].lower() == preference_filter.lower()]
    else:
        filtered = all_dests

    return render_template('destinations.html', destinations=filtered, current_filter=preference_filter)


# Route 9: User Authentication (Login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')

            # Check if user had a pending trip save action
            if 'pending_save' in session:
                pending = session.pop('pending_save')
                save_user_trip(
                    user_id=user['id'],
                    destination_id=int(pending['destination_id']),
                    start_location=pending.get('start_location', 'City'),
                    budget=float(pending.get('budget', 0)),
                    days=int(pending.get('days', 1)),
                    travelers=int(pending.get('travelers', 1)),
                    preference=pending.get('preference', 'General'),
                    total_cost=float(pending.get('total_cost', 0)),
                    remaining_budget=float(pending.get('remaining_budget', 0))
                )
                flash('Your planned trip was automatically saved to your dashboard!', 'success')
                return redirect(url_for('my_trips'))

            return redirect(url_for('my_trips'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


# Route 10: User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registers a new user account.
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'warning')
            return render_template('register.html')

        user_id = create_user(name, email, password)
        if user_id:
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            flash('Account created successfully! Welcome to Smart Trip Planner.', 'success')

            if 'pending_save' in session:
                pending = session.pop('pending_save')
                save_user_trip(
                    user_id=user_id,
                    destination_id=int(pending['destination_id']),
                    start_location=pending.get('start_location', 'City'),
                    budget=float(pending.get('budget', 0)),
                    days=int(pending.get('days', 1)),
                    travelers=int(pending.get('travelers', 1)),
                    preference=pending.get('preference', 'General'),
                    total_cost=float(pending.get('total_cost', 0)),
                    remaining_budget=float(pending.get('remaining_budget', 0))
                )
                flash('Your planned trip was saved to your new account!', 'success')
                return redirect(url_for('my_trips'))

            return redirect(url_for('plan'))
        else:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

    return render_template('register.html')


# Route 11: Logout
@app.route('/logout')
def logout():
    """Logs out the current user and clears session credentials."""
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Initialize DB on first startup
    init_db()
    # Run development server on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
