from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Area(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='areas')
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('location', 'name')

    def __str__(self):
        return f"{self.name} ({self.location.name})"

class Space(models.Model):
    name = models.CharField(max_length=255)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='spaces')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0.0)
    facilities = models.TextField(blank=True, null=True) # Comma separated
    image = models.CharField(max_length=255, blank=True, null=True)
    booking_rooms_details = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.area.name}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='bookings')
    
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    date = models.DateField()
    time_slot = models.CharField(max_length=100)
    duration = models.CharField(max_length=100, blank=True, null=True)
    seats = models.IntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=50, default='Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.space.name} on {self.date}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'space')

    def __str__(self):
        return f"{self.user.username} favorited {self.space.name}"
