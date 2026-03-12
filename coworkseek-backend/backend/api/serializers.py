from rest_framework import serializers
from .models import Location, Area, Space, Booking, Favorite
from django.contrib.auth.models import User

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    
    class Meta:
        model = Area
        fields = ('id', 'location', 'location_name', 'name')

class SpaceSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.name', read_only=True)
    area = serializers.CharField(source='area.name', read_only=True)
    location_name = serializers.CharField(source='area.location.name', read_only=True)
    city_name = serializers.CharField(source='area.location.name', read_only=True)
    location_id = serializers.IntegerField(source='area.location.id', read_only=True)
    is_favorite = serializers.SerializerMethodField()
    facilities_list = serializers.SerializerMethodField()

    class Meta:
        model = Space
        fields = '__all__'

    def get_is_favorite(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, space=obj).exists()
        return False

    def get_facilities_list(self, obj):
        if obj.facilities:
            return [f.strip() for f in obj.facilities.split(',')]
        return []

class BookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    space_name = serializers.CharField(source='space.name', read_only=True)
    space_details = SpaceSerializer(source='space', read_only=True)

    class Meta:
        model = Booking
        fields = ('id', 'user', 'user_name', 'space', 'space_name', 'space_details', 'full_name', 'email', 'phone', 'date', 'time_slot', 'duration', 'seats', 'notes', 'status', 'created_at')
        read_only_fields = ('user',)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'confirm_password', 'first_name', 'last_name')

    def validate(self, data):
        if 'confirm_password' in data and data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class FavoriteSerializer(serializers.ModelSerializer):
    space_details = SpaceSerializer(source='space', read_only=True)
    
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'space', 'space_details', 'created_at')
        read_only_fields = ('user',)
