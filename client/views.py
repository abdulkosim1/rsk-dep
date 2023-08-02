from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
import uuid
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from services import constants
from services.authentication import ClientTokenAuthentication
from apps.talon.serializers import TalonSerializer
from services.permissions import IsOwner
from apps.talon.models import Talon
from services.utils import normalize_phone

from .models import Client, CustomToken
from .serializers import (
    RegistrationSerializer,
    ActivationSerializer,
    RestorePasswordSerializer,
    SetRestoredPasswordSerializer
    )


class RegistrationView(APIView):
    def post(self, request: Request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                'Thanks for registration! Activate your account',
                status=status.HTTP_201_CREATED
                )


class ActivationView(APIView):
    def post(self, request: Request):
        serializer = ActivationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.activate_account()
            return Response(
                'Аккаунт активирован!',
                status=status.HTTP_200_OK
            )

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [ClientTokenAuthentication]

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        try:
            phone = normalize_phone(phone)
            client = get_object_or_404(Client, phone=phone)
        except Client.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=401)

        if not client.check_password(password):
            return Response({'error': 'Invalid credentials.'}, status=401)

        try:
            previous_token = CustomToken.objects.get(client=client)
            previous_token.delete()
        except CustomToken.DoesNotExist:
            pass

        access_token = CustomToken.objects.create(key=str(uuid.uuid4()), client=client)

        refresh = RefreshToken.for_user(client)

        return Response({
            'access_token': access_token.key,
            'refresh_token': str(refresh),
        })


class ClientTalosView(ListAPIView):
    serializer_class = TalonSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [ClientTokenAuthentication]

    def get_queryset(self):
        queryset = Talon.objects.filter(client=self.request.user, status__in=[constants.TALON_STATUS_WAITING,constants.TALON_STATUS_INSERVICE])
        return queryset


class RemoveClientTalonsView(APIView):
    serializer_class = TalonSerializer
    permission_classes = [IsOwner]
    authentication_classes = [ClientTokenAuthentication]

    def get(self, request:Request, pk):
        talon = Talon.objects.filter(client=self.request.user, id=pk)
        talon.status = constants.TALON_STATUS_CANCELED
        return Response('Талон отменен',
                status=status.HTTP_204_NO_CONTENT)


class RestorePasswordView(APIView):
    
    @swagger_auto_schema(request_body=RestorePasswordSerializer)
    def post(self, request: Request):
        serializer = RestorePasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.send_code()
            return Response(
                'СМС с кодом для восстановления пароля был отправлен на ваш номер.',
                status=status.HTTP_200_OK
            )


class SetRestoredPasswordView(APIView):

    @swagger_auto_schema(request_body=SetRestoredPasswordSerializer)
    def post(self, request: Request):
        serializer = SetRestoredPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.set_new_password()
            return Response(
                'Ваш пароль успешно восстановлен.',
                status=status.HTTP_200_OK
            )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [ClientTokenAuthentication]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            
            user = Client.objects.get(id=refresh.payload.get('user_id'))
        except TokenError:
            return Response({'error': 'Invalid refresh token.'}, status=401)
        except Client.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        try:
            custom_token = CustomToken.objects.get(client=user)
            custom_token.delete()
        except CustomToken.DoesNotExist:
            pass

        access_token = CustomToken.objects.create(key=str(uuid.uuid4()), client=user)
        return Response({'access_token': str(access_token)})