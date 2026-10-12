"""
Smart Trip Planner - Recommendation Engine & Itinerary Generator
Implements transparent scoring logic and dynamic day-by-day travel plan synthesis.
"""

import math


def calculate_trip_cost(destination, days, travelers):
    """
    Calculate itemized estimated trip costs based on travelers and duration.
    Rooms needed assumes 2 travelers per standard room (rounded up).
    """
    rooms = math.ceil(travelers / 2)
    
    # 1. Transportation cost (round trip / transit estimated per traveler)
    transport_cost = destination['transport_cost'] * travelers
    
    # 2. Hotel accommodation cost (rooms * daily rate * days)
    hotel_cost = destination['hotel_per_day'] * rooms * days
    
    # 3. Food and dining cost (daily allowance * travelers * days)
    food_cost = destination['food_per_day'] * travelers * days
    
    # 4. Sightseeing and activities cost (entry fees, tickets, tours per traveler)
    activity_cost = destination['activity_cost'] * travelers
    
    # 5. Miscellaneous buffer (local transit, auto-rickshaw, snacks, 5% of hotel+food+activities)
    misc_cost = round(0.05 * (hotel_cost + food_cost + activity_cost))
    
    total_cost = transport_cost + hotel_cost + food_cost + activity_cost + misc_cost
    
    return {
        'transport_cost': transport_cost,
        'hotel_cost': hotel_cost,
        'food_cost': food_cost,
        'activity_cost': activity_cost,
        'misc_cost': misc_cost,
        'total_cost': total_cost,
        'rooms': rooms
    }


def calculate_suitability(destination, budget, days, travelers, preference):
    """
    Calculate the transparent recommendation suitability score (0 to 100).
    Score = Budget Match (40 pts) + Days Match (30 pts) + Preference Match (30 pts)
    """
    cost_data = calculate_trip_cost(destination, days, travelers)
    total_cost = cost_data['total_cost']
    remaining_budget = budget - total_cost
    min_days = destination['min_days']
    
    # --- 1. Budget Match Score (Max 40 points) ---
    if total_cost <= budget:
        # Destination is fully affordable
        utilization = total_cost / budget
        if 0.70 <= utilization <= 0.98:
            # Optimal utilization of available budget
            budget_score = 40.0
        elif utilization >= 0.50:
            # Good value with comfortable buffer
            budget_score = 35.0
        else:
            # Under budget (very economical), leaves substantial surplus
            budget_score = 30.0
    else:
        # Destination slightly or significantly exceeds budget
        over_ratio = (total_cost - budget) / budget
        if over_ratio <= 0.10:
            budget_score = 22.0  # Just 10% over budget
        elif over_ratio <= 0.25:
            budget_score = 12.0  # 25% over budget
        else:
            budget_score = 4.0   # Significantly over budget

    # --- 2. Days Match Score (Max 30 points) ---
    day_diff = days - min_days
    if day_diff == 0:
        # Exact match with ideal duration
        days_score = 30.0
    elif day_diff == 1:
        # 1 extra day offers a relaxed, comfortable exploration pace
        days_score = 28.0
    elif day_diff > 1:
        # Extra leisure days
        days_score = 24.0
    else:
        # Trip duration is shorter than recommended minimum (rushed)
        shortfall = abs(day_diff)
        if shortfall == 1:
            days_score = 16.0
        else:
            days_score = 8.0

    # --- 3. Preference Match Score (Max 30 points) ---
    dest_pref = destination['preference'].strip().lower()
    user_pref = preference.strip().lower()
    
    if user_pref == 'any' or user_pref == 'all' or user_pref == dest_pref:
        preference_score = 30.0
        pref_match_label = "Exact Theme Match"
    else:
        # Complementary cross-interest points (e.g. Nature lovers often enjoy Adventure)
        complementary = {
            'nature': ['adventure', 'beach'],
            'adventure': ['nature'],
            'historical': ['religious'],
            'religious': ['historical'],
            'beach': ['nature', 'adventure']
        }
        if user_pref in complementary and dest_pref in complementary[user_pref]:
            preference_score = 18.0
            pref_match_label = "Complementary Theme"
        else:
            preference_score = 10.0
            pref_match_label = "Alternative Spot"

    # Total score calculation
    total_score = round(budget_score + days_score + preference_score, 1)

    # Human-readable "Why this destination is suitable" reason synthesis
    reasons = []
    
    # Budget reason
    if remaining_budget >= 0:
        if remaining_budget > 0:
            reasons.append(f"Comfortably fits your ₹{budget:,.0f} budget with ₹{remaining_budget:,.0f} surplus savings")
        else:
            reasons.append(f"Maximizes your ₹{budget:,.0f} budget without overspending")
    else:
        reasons.append(f"Slightly above budget by ₹{abs(remaining_budget):,.0f}, but provides exceptional value")
        
    # Days reason
    if days >= min_days:
        reasons.append(f"Your {days}-day plan offers ample time to explore key sights (recommended: {min_days} days)")
    else:
        reasons.append(f"Can be covered in a fast-paced {days}-day weekend visit")

    # Preference reason
    if pref_match_label == "Exact Theme Match" and user_pref not in ['any', 'all']:
        reasons.append(f"Top-rated {destination['preference']} destination in {destination['state']}")
    else:
        reasons.append(f"Renowned destination in {destination['state']} offering diverse experiences")

    why_suitable = ". ".join(reasons) + "."

    return {
        'destination': destination,
        'suitability_score': total_score,
        'budget_score': budget_score,
        'days_score': days_score,
        'preference_score': preference_score,
        'cost_data': cost_data,
        'remaining_budget': remaining_budget,
        'why_suitable': why_suitable,
        'pref_match_label': pref_match_label
    }


def get_top_recommendations(destinations, budget, days, travelers, preference, limit=3):
    """
    Score all destinations and return the top 3 best matching destinations.
    """
    scored = []
    for dest in destinations:
        result = calculate_suitability(dest, budget, days, travelers, preference)
        scored.append(result)
        
    # Sort primarily by suitability score descending, then by remaining budget descending
    scored.sort(key=lambda x: (x['suitability_score'], x['remaining_budget']), reverse=True)
    
    return scored[:limit]


def generate_itinerary(destination, days, start_location="Starting City"):
    """
    Synthesize an intuitive, engaging day-by-day travel itinerary
    customized to the trip duration and destination attractions.
    """
    highlights_raw = destination['highlights'] if 'highlights' in destination.keys() else ""
    attractions = [item.strip() for item in highlights_raw.split(',') if item.strip()]
    dest_name = destination['name']
    
    # Fallback attractions if list is small
    default_attractions = [
        f"{dest_name} Scenic Viewpoint",
        f"Central {dest_name} Heritage Market",
        f"{dest_name} Nature Trail & Garden",
        f"Historic Landmarks of {dest_name}",
        f"{dest_name} Cultural Center & Evening Show"
    ]
    
    pool = attractions + [a for a in default_attractions if a not in attractions]
    
    itinerary = []
    
    for day in range(1, days + 1):
        if day == 1:
            # Day 1: Journey, Arrival, Orientation
            first_spot = pool[0] if len(pool) > 0 else f"{dest_name} Viewpoint"
            day_plan = {
                'day': 1,
                'title': f"Arrival & Welcome to {dest_name}",
                'morning': f"Depart from {start_location}. Scenic journey to {dest_name} via comfortable transit.",
                'afternoon': f"Check-in at hotel, refresh, and enjoy traditional authentic {destination['state']} lunch.",
                'evening': f"Leisure stroll to {first_spot}. Experience the serene sunset and local evening atmosphere."
            }
        elif day == days:
            # Last Day: Souvenirs, final sightseeing, return journey
            last_spot = pool[(day - 1) % len(pool)]
            day_plan = {
                'day': day,
                'title': f"Memories & Return Journey",
                'morning': f"Morning visit to {last_spot} for early photography and peaceful scenery.",
                'afternoon': f"Souvenir shopping at local bazaars, pick up regional specialties and check out from accommodation.",
                'evening': f"Head to transit terminal. Safe and comfortable return journey back to {start_location}."
            }
        elif day == 2:
            # Day 2: Primary sightseeing tour
            spot_1 = pool[1 % len(pool)]
            spot_2 = pool[2 % len(pool)]
            day_plan = {
                'day': 2,
                'title': f"Signature Sightseeing & Exploration",
                'morning': f"Hearty breakfast followed by guided visit to {spot_1}.",
                'afternoon': f"Delight in regional cuisine followed by exploration of {spot_2}.",
                'evening': f"Sunset viewpoint photography, cafe hopping, and sampling famous street foods."
            }
        elif day == 3:
            # Day 3: Adventure / Cultural immersion
            spot_3 = pool[3 % len(pool)]
            spot_4 = pool[4 % len(pool)]
            day_plan = {
                'day': 3,
                'title': f"Adventure & Nature Immersion",
                'morning': f"Early morning nature walk or excursion to {spot_3}.",
                'afternoon': f"Picnic lunch or riverside cafe dining. Afternoon visit to {spot_4}.",
                'evening': f"Cultural performance or bonfire dinner session under starlit skies."
            }
        else:
            # Days 4+: Extended discovery
            spot_n = pool[(day) % len(pool)]
            day_plan = {
                'day': day,
                'title': f"Offbeat Discovery & Leisure",
                'morning': f"Visit scenic offbeat spot: {spot_n}.",
                'afternoon': f"Relaxing lunch, wellness activity or local village craft immersion.",
                'evening': f"Free time for photography, local market interaction, and relaxed dinner."
            }
            
        itinerary.append(day_plan)
        
    return itinerary
