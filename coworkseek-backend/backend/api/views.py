from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import City, SpaceType, Space, Booking, Favorite
from .serializers import CitySerializer, SpaceTypeSerializer, SpaceSerializer, BookingSerializer, UserSerializer, FavoriteSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class SpaceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SpaceType.objects.all()
    serializer_class = SpaceTypeSerializer

class SpaceViewSet(viewsets.ModelViewSet):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer

    def get_queryset(self):
        queryset = Space.objects.all()
        city = self.request.query_params.get('city', None)
        space_type = self.request.query_params.get('space_type', None)
        listed_by = self.request.query_params.get('listed_by', None)

        if city:
            if city.isdigit():
                queryset = queryset.filter(city_id=city)
            else:
                queryset = queryset.filter(city__name__iexact=city)
        if space_type:
            queryset = queryset.filter(space_type__slug=space_type)
        
        if listed_by == 'me' and self.request.user.is_authenticated:
            queryset = queryset.filter(listed_by=self.request.user)
        elif listed_by:
            queryset = queryset.filter(listed_by_id=listed_by)
            
        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(listed_by=self.request.user)
        else:
            serializer.save()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        space_id = request.data.get('space_id')
        if not space_id:
            return Response({'error': 'space_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        favorite = Favorite.objects.filter(user=request.user, space_id=space_id).first()
        if favorite:
            favorite.delete()
            return Response({'status': 'removed', 'is_favorite': False})
        else:
            Favorite.objects.create(user=request.user, space_id=space_id)
            return Response({'status': 'added', 'is_favorite': True})
