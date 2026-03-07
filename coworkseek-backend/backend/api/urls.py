from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, SpaceTypeViewSet, SpaceViewSet, BookingViewSet, UserViewSet, FavoriteViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'space-types', SpaceTypeViewSet)
router.register(r'spaces', SpaceViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'users', UserViewSet, basename='user')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]
