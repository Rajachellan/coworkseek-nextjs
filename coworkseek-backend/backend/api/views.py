from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Location, Area, Space, Booking, Favorite, Contact
from .serializers import (
    LocationSerializer, AreaSerializer, SpaceSerializer, 
    BookingSerializer, UserSerializer, FavoriteSerializer, ContactSerializer
)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

    def get_queryset(self):
        queryset = Area.objects.all()
        location_id = self.request.query_params.get('location', None)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        return queryset

class SpaceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer

    def get_queryset(self):
        queryset = Space.objects.all()
        location_id = self.request.query_params.get('location', None)
        area_id = self.request.query_params.get('area', None)
        city = self.request.query_params.get('city', None)
        search = self.request.query_params.get('search', None)

        if location_id:
            queryset = queryset.filter(area__location_id=location_id)
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        if city:
            queryset = queryset.filter(area__location__name__iexact=city)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
            
        return queryset

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
        identity = request.data.get('username') # Looking at 'username' field which acts as 'identity'
        password = request.data.get('password')
        
        if not identity or not password:
            return Response({'error': 'Identity and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if identity is an email
        if '@' in identity:
            user_obj = User.objects.filter(email=identity).first()
            if user_obj:
                username = user_obj.username
            else:
                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            username = identity

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

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        logout(request)
        return Response({'success': 'Logged out successfully'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        data = serializer.data
        data['bookings_count'] = Booking.objects.filter(user=request.user).count()
        data['favorites_count'] = Favorite.objects.filter(user=request.user).count()
        return Response(data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def password_reset(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            
            # Use console backend by default in settings
            send_mail(
                'Password Reset for CoworkSeek',
                f'Please use the following link to reset your password: {reset_url}',
                'noreply@coworkseek.com',
                [email],
                fail_silently=False,
            )
            
        # We return 200 even if user doesn't exist for security (avoid email enumeration)
        return Response({'success': 'Password reset email sent if account exists.'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def password_reset_confirm(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([uidb64, token, new_password]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'success': 'Password has been reset successfully.'})
        else:
            return Response({'error': 'Invalid reset link or token'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch', 'put'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        user = request.user
        data = request.data
        
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
            
        user.save()
        return Response(UserSerializer(user).data)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post'] # Only allow POST

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
