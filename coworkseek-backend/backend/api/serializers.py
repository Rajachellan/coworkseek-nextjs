from rest_framework import serializers
from .models import City, SpaceType, Space, Booking, Favorite
from django.contrib.auth.models import User

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'image', 'tagline', 'description')

class SpaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceType
        fields = '__all__'

class SpaceSerializer(serializers.ModelSerializer):
    city_name = serializers.ReadOnlyField(source='city.name')
    city_image = serializers.ImageField(source='city.image', read_only=True)
    city_id = serializers.ReadOnlyField(source='city.id')
    space_type_name = serializers.ReadOnlyField(source='space_type.name')
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = '__all__'

    def get_is_favorite(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, space=obj).exists()
        return False

class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    space_name = serializers.ReadOnlyField(source='space.name')

    class Meta:
        model = Booking
        fields = ('id', 'user', 'user_name', 'space', 'space_name', 'booking_date', 'booking_time', 'status', 'created_at')

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class FavoriteSerializer(serializers.ModelSerializer):
    space_details = SpaceSerializer(source='space', read_only=True)
    
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'space', 'space_details', 'created_at')
        read_only_fields = ('user',)
