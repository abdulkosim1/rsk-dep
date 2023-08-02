from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import date

from main.services import constants
from main.services.permissions import IsOperatorOrRegistrator
from stats.models import Actions
from talon.models import Talon
from . serializers import (
    UserSerializer, 
    OperatorQueueSerializer, 
    CustomTokenObtainPairSerializer,
    RegistratorQueueSerializer,
    )

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

class UserRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request:Request):
        user = get_object_or_404(User, id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class OperatorQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operator_queue = Talon.objects.filter(
            branch=request.user.branch,
            service__in=request.user.service.all(),
            status__in=[constants.TALON_STATUS_WAITING, constants.TALON_STATUS_INSERVICE],
            appointment_date__date=date.today(),
        ).order_by('appointment_date')
        serializer = OperatorQueueSerializer(operator_queue, context={'request': request})
        return Response(serializer.data)


class RegistratorQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request:Request):
        registrator_queue = Talon.objects.filter(branch=request.user.branch).order_by('appointment_date')
        serializer = RegistratorQueueSerializer(registrator_queue, context={'request': request})
        return Response(serializer.data)


class EmployeeShiftView(APIView):
    permission_classes = [IsOperatorOrRegistrator]

    def get(self, request:Request):
        employee = request.user
        status = employee.status
        if employee.status == constants.EMPLOYEE_STATUS_INACTIVE:
            employee.status = constants.EMPLOYEE_STATUS_ACTIVE
        elif employee.status == constants.EMPLOYEE_STATUS_ACTIVE:
            employee.status = constants.EMPLOYEE_STATUS_INACTIVE
        employee.save()

        Actions.objects.create(
                employee=request.user,
                action= f'status changed from "{status}" to "{employee.status}"',
                branch=request.user.branch
                )
        return Response('Статус Изменен')