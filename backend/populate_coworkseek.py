import os
import django
import random
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import Location, Area, Space, Booking, Favorite
from django.contrib.auth.models import User

def populate():
    locations_data = [
        {"name": "Chennai", "areas": ["Anna Nagar", "Guindy", "T Nagar", "Velachery"]},
        {"name": "Hyderabad", "areas": ["Gachibowli", "HITEC City", "Banjara Hills", "Jubilee Hills"]},
        {"name": "Bangalore", "areas": ["Koramangala", "Indiranagar", "HSR Layout", "Whitefield"]},
        {"name": "Mumbai", "areas": ["Andheri", "Bandra", "Worli", "Powai"]},
        {"name": "Delhi", "areas": ["Connaught Place", "Saket", "Hauz Khas", "Dwarka"]},
        {"name": "Pune", "areas": ["Baner", "Hinjewadi", "Viman Nagar", "Koregaon Park"]},
        {"name": "Kolkata", "areas": ["Salt Lake", "New Town", "Park Street", "Ballygunge"]},
        {"name": "Ahmedabad", "areas": ["Prahlad Nagar", "Satellite", "SG Highway", "Navrangpura"]},
        {"name": "Gurgaon", "areas": ["Cyber City", "Udyog Vihar", "Golf Course Road", "Sohna Road"]},
        {"name": "Noida", "areas": ["Sector 62", "Sector 18", "Sector 150", "Greater Noida"]},
        {"name": "Kochi", "areas": ["Kakkanad", "Edappally", "Fort Kochi", "MG Road"]},
        {"name": "Jaipur", "areas": ["Malviya Nagar", "Vaishali Nagar", "C-Scheme", "Mansarovar"]},
    ]

    facilities_samples = [
        "High-Speed Wi-Fi, Coffee/Tea, Parking, Power Backup, Meeting Rooms",
        "Wi-Fi, AC, Print/Scan, Lounge Area, Cafeteria",
        "Ergonomic Chairs, Standing Desks, High-Speed Internet, Gym Access",
        "24/7 Access, Security, Reception, Cleaning Services, Mail Handling"
    ]

    print("Cleaning database...")
    Booking.objects.all().delete()
    Favorite.objects.all().delete()
    Space.objects.all().delete()
    Area.objects.all().delete()
    Location.objects.all().delete()

    for loc_info in locations_data:
        location = Location.objects.create(
            name=loc_info["name"],
            description=f"Discover premium coworking spaces in {loc_info['name']}.",
            image=f"https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&q=80&w=1000"
        )
        print(f"Created Location: {location.name}")

        for area_name in loc_info["areas"]:
            area = Area.objects.create(location=location, name=area_name)
            
            # Create a few spaces per area
            for i in range(1, 4):
                space = Space.objects.create(
                    name=f"{area_name} Hub {i}",
                    area=area,
                    price=random.randint(500, 2000),
                    rating=round(random.uniform(3.5, 5.0), 1),
                    facilities=random.choice(facilities_samples),
                    booking_rooms_details=f"Desk Space · {random.randint(1, 10)} Seater",
                    description=f"A premium coworking space located in the heart of {area_name}, {location.name}.",
                    image=f"https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=1000"
                )
    
    print("Population complete!")

if __name__ == "__main__":
    populate()
