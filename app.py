from flask import Flask, render_template, request, redirect, url_for, session
import datetime

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-key"

# In-memory mock data
AVAILABLE_DESTINATIONS = [
    "Low Earth Orbit Station",
    "Moon Base Alpha",
    "Mars Transit Hub",
    "Orbital Luxury Resort"
]

SEAT_CLASSES = [
    "Economy Shuttle",
    "Luxury Cabin",
    "VIP Zero-Gravity Suite"
]

# Pricing & Packages details
PACKAGES = {
    "Economy Shuttle": {
         "price": "$100,000",
         "description": "Affordable shuttle service to orbit with basic amenities."
    },
    "Luxury Cabin": {
         "price": "$250,000",
         "description": "Premium cabin with comfortable seating and gourmet meals."
    },
    "VIP Zero-Gravity Suite": {
         "price": "$500,000",
         "description": "Experience zero-gravity in style with a private suite and exclusive services."
    }
}

# Accommodation options per destination
ACCOMMODATIONS = {
    "Low Earth Orbit Station": ["Orbit Hotel", "Zero-G Comfort Suites"],
    "Moon Base Alpha": ["Moonlight Resort", "Lunar Lodge"],
    "Mars Transit Hub": ["Red Desert Hotel", "Martian Oasis"],
    "Orbital Luxury Resort": ["Galactic Palace", "Starview Retreat"]
}

# Store bookings in a list for simplicity
bookings = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        departure_date_str = request.form.get("departure_date")
        destination = request.form.get("destination")
        seat_class = request.form.get("seat_class")
        user_name = request.form.get("user_name")
        
        try:
            departure_date = datetime.datetime.strptime(departure_date_str, "%Y-%m-%d").date()
        except ValueError:
            departure_date = None
        
        # Retrieve pricing information based on selected seat class
        price = PACKAGES.get(seat_class, {}).get("price", "N/A")
        
        new_booking = {
            "user_name": user_name,
            "departure_date": departure_date,
            "destination": destination,
            "seat_class": seat_class,
            "price": price,
            "booking_id": len(bookings) + 1
        }
        bookings.append(new_booking)
        session["user_name"] = user_name
        return redirect(url_for("dashboard"))
    else:
        return render_template(
            "booking.html",
            destinations=AVAILABLE_DESTINATIONS,
            seat_classes=SEAT_CLASSES
        )

@app.route("/pricing")
def pricing():
    # Display pricing & package details
    return render_template("pricing.html", packages=PACKAGES)

@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    if request.method == "POST":
        chosen_destination = request.form.get("destination_pref")
        # Use the ACCOMMODATIONS dictionary to fetch suggestions based on the destination.
        recommended_accommodations = ACCOMMODATIONS.get(chosen_destination, [])
        return render_template(
            "recommendations.html",
            destinations=AVAILABLE_DESTINATIONS,
            chosen_destination=chosen_destination,
            recommended_accommodations=recommended_accommodations
        )
    else:
        return render_template(
            "recommendations.html",
            destinations=AVAILABLE_DESTINATIONS,
            chosen_destination=None,
            recommended_accommodations=None
        )

@app.route("/dashboard")
def dashboard():
    user_name = session.get("user_name", None)
    if not user_name:
        return redirect(url_for("booking"))
    
    # Filter bookings for the current user
    user_bookings = [b for b in bookings if b["user_name"] == user_name]
    
    # AI-based travel tips per seat class
    travel_tips = {
        "Economy Shuttle": "Bring space-friendly snacks; you’ll love the view from the large cabin windows.",
        "Luxury Cabin": "Expect premium cosmic cuisine and private sleeping pods.",
        "VIP Zero-Gravity Suite": "Enjoy your personal AI butler, plus curated cosmic entertainment."
    }
    
    now = datetime.date.today()
    dashboard_data = []
    for b in user_bookings:
        if b["departure_date"]:
            days_left = (b["departure_date"] - now).days
        else:
            days_left = "N/A"
        tip = travel_tips.get(b["seat_class"], "Enjoy your journey through space!")
        dashboard_data.append({
            "booking_id": b["booking_id"],
            "destination": b["destination"],
            "departure_date": b["departure_date"],
            "days_left": days_left,
            "seat_class": b["seat_class"],
            "price": b["price"],
            "tip": tip
        })
    
    return render_template(
        "dashboard.html",
        user_name=user_name,
        dashboard_data=dashboard_data
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
