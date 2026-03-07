from django.db import models
from django.contrib.auth.models import User

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='cities/', null=True, blank=True)
    tagline = models.CharField(max_length=255, null=True, blank=True, help_text="e.g., The Silicon Valley of India")
    description = models.TextField(null=True, blank=True, help_text="Rich storytelling about the city vibe")

    def __str__(self):
        return self.name

class SpaceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Space(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='spaces')
    area = models.CharField(max_length=255)
    space_type = models.ForeignKey(SpaceType, on_delete=models.CASCADE, related_name='spaces')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='spaces/')
    bookspace = models.CharField(max_length=255, help_text="e.g., Meeting Rooms · 6 Seater")
    tag = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listed_spaces', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.city.name}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.space.name} on {self.booking_date}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'space')

    def __str__(self):
        return f"{self.user.username} - {self.space.name}"
