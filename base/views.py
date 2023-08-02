from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from main.services.authentication import ClientTokenAuthentication
from talon.serializers import TerminalTalonCreateSerializer
from . models import Document, Terminal, Service
from .serializers import (
    TerminalSerializer, 
    TerminalAuthSerializer, 
    DocumentSerializer, 
    ServiceSerializer,
    )


class DocumentListView(ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentRetrieveView(APIView):
    def get(self, request:Request,pk:int):
        document = get_object_or_404(Document, id=pk)
        serializer = DocumentSerializer(document)
        return Response(serializer.data)


class TerminalListView(APIView):

    def get(self, request:Request):
        terminals = Terminal.objects.all()
        serializer = TerminalSerializer(terminals, many=True)
        return Response(serializer.data)


class TerminalLoginView(APIView):
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'pc_name': openapi.Schema(type=openapi.TYPE_STRING),
                'pin': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['pc_name', 'pin'],
        ),
        responses={
            201: openapi.Response(
                description='Successful login',
                content={'application/json': {'schema': {'token': openapi.Schema(type=openapi.TYPE_STRING)}}},
            ),
            400: 'Bad Request',
            401: 'Unauthorized',
        },
    )
    def post(self, request:Request):
        pc_name = request.data.get('pc_name', '')
        pin = request.data.get('pin', '')

        try:
            terminal = Terminal.objects.get(pc_name=pc_name)
        except Terminal.DoesNotExist:
            raise AuthenticationFailed('Invalid PC name')

        if not terminal.pin == pin:
            raise AuthenticationFailed('Invalid PIN')

        terminal.generate_token()
        terminal.save()

        return Response({'token': terminal.auth_token})


class TerminalLogoutView(APIView):

    def post(self, token:str):
        try:
            terminal = Terminal.objects.get(token=token)
        except Terminal.DoesNotExist:
            raise AuthenticationFailed('Not authenticated')
        else:
            terminal.token.delete()


class TerminalGetTalon(APIView):
    
    def post(self, request:Request):
        terminal_serializer = TerminalAuthSerializer(data=request.data)
        print(request.user)
        talon_serializer = TerminalTalonCreateSerializer(data=request.data)
        if terminal_serializer.is_valid(raise_exception=True) and talon_serializer.is_valid(raise_exception=True) :
            talon_serializer.save()
            return Response(talon_serializer.data)


class ServiceListView(ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    authentication_classes = [ClientTokenAuthentication]
    permission_classes = [IsAuthenticated]


class ServiceRetrieveView(APIView):
    def get(self, request:Request, pk:int):
        branch = Service.objects.get(pk=pk)
        serializer = ServiceSerializer(branch)
        return Response(serializer.data)