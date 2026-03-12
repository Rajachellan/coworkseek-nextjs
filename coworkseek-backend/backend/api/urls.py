from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationViewSet, AreaViewSet, SpaceViewSet, 
    BookingViewSet, UserViewSet, FavoriteViewSet
)

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'areas', AreaViewSet)
router.register(r'spaces', SpaceViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'users', UserViewSet, basename='user')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]
