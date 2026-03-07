import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import City, SpaceType, Space

def populate():
    # Cities mapping with images
    city_configs = [
        {"name": "Chennai", "image": "cities/chennai.jpg"},
        {"name": "Bangalore", "image": "cities/bangalore.jpg"},
        {"name": "Coimbatore", "image": "cities/coimbatore.jpg"},
        {"name": "Noida", "image": "cities/noida.jpg"},
        {"name": "Delhi", "image": "cities/delhi.jpg"},
        {"name": "Mumbai", "image": "cities/mumbai.jpg"},
        {"name": "Pune", "image": "cities/pune.jpg"},
        {"name": "Hyderabad", "image": "cities/hyderabad.jpg"},
        {"name": "Kolkata", "image": "cities/kolkatta.jpg"},
        {"name": "Gurgaon", "image": "cities/gurgaon.jpg"},
    ]
    
    cities = {}
    for cfg in city_configs:
        city, _ = City.objects.get_or_create(name=cfg["name"])
        city.image = cfg["image"]
        city.save()
        cities[cfg["name"].lower()] = city

    # Space Types
    meeting_rooms, _ = SpaceType.objects.get_or_create(name="Meeting Rooms", slug="meeting-rooms")
    hot_desks, _ = SpaceType.objects.get_or_create(name="Hot Desks", slug="hot-desks")
    private_cabin, _ = SpaceType.objects.get_or_create(name="Private Cabin", slug="private-cabin")
    virtual_office, _ = SpaceType.objects.get_or_create(name="Virtual Office", slug="virtual-office")
    studio, _ = SpaceType.objects.get_or_create(name="Studio", slug="studio")
    dedicated_desk, _ = SpaceType.objects.get_or_create(name="Dedicated Desk", slug="dedicated-desk")

    # Helper for spaces
    spaces_data = []

    # Add Meeting Rooms to all cities
    for city_name, city_obj in cities.items():
        spaces_data.append({
            "name": f"Elite {city_name.capitalize()} Workspace",
            "city": city_obj,
            "area": "Business District",
            "space_type": meeting_rooms,
            "price": 1500,
            "bookspace": "Meeting Rooms · 8 Seater",
            "tag": "Premium",
            "image": f"cities/{city_name if city_name != 'kolkata' else 'kolkatta'}.jpg"
        })

    # Add Hot Desks to all cities
    for city_name, city_obj in cities.items():
        spaces_data.append({
            "name": f"Flexi Hub {city_name.capitalize()}",
            "city": city_obj,
            "area": "Tech Park",
            "space_type": hot_desks,
            "price": 499,
            "bookspace": "Hot Desk",
            "tag": "Popular",
            "image": f"cities/{city_name if city_name != 'kolkata' else 'kolkatta'}.jpg"
        })

    # Add Private Cabins to major cities
    for city_name in ["mumbai", "bangalore", "chennai", "delhi"]:
        if city_name in cities:
            spaces_data.append({
                "name": f"Private Suite {city_name.capitalize()}",
                "city": cities[city_name],
                "area": "Downtown",
                "space_type": private_cabin,
                "price": 15000,
                "bookspace": "Private Cabin · 4 Seater",
                "tag": "Luxury",
                "image": f"cities/{city_name}.jpg"
            })

    for space_data in spaces_data:
        Space.objects.update_or_create(
            name=space_data["name"],
            city=space_data["city"],
            defaults={
                "area": space_data["area"],
                "space_type": space_data["space_type"],
                "price": space_data["price"],
                "bookspace": space_data["bookspace"],
                "tag": space_data.get("tag"),
                "image": space_data["image"]
            }
        )
    
    print("Database populated successfully with city images and spaces!")

if __name__ == '__main__':
    populate()
