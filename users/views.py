from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from django.utils.crypto import get_random_string
import requests
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
)
from .throttling import LoginRateThrottle, RegisterRateThrottle
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

# Create your views here.

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
    throttle_classes = [RegisterRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        # Check if the email exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Le mot de passe est incorrect.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class CheckTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(status=status.HTTP_200_OK)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        id_token = request.data.get('id_token')
        if not id_token:
            return Response({'error': 'id_token is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the token with Google
        google_client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
        verify_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
        try:
            resp = requests.get(verify_url)
            if resp.status_code != 200:
                return Response({'error': 'Invalid Google token'}, status=status.HTTP_401_UNAUTHORIZED)
            payload = resp.json()
        except Exception as e:
            return Response({'error': f'Could not verify token: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Check audience
        if payload.get('aud') != google_client_id:
            return Response({'error': 'Token audience does not match'}, status=status.HTTP_401_UNAUTHORIZED)

        email = payload.get('email')
        sub = payload.get('sub')
        name = payload.get('name', '')
        picture_url = payload.get('picture')
        if not email or not sub:
            return Response({'error': 'Google token missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            # Optionally, check if user is a Google user (e.g., by a flag or field)
        except User.DoesNotExist:
            # Create a new user
            user = User.objects.create_user(
                profile_picture=picture_url,
                username=name,
                email=email,
                password=get_random_string(32),
                first_name=name
            )
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
