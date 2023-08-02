from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.response import Response
from admin_panel.models import Report
from django.contrib.auth import get_user_model
from rest_framework import mixins,status
from django.shortcuts import get_object_or_404
from django.http import Http404

from branch.serializers import AdvertisementSerilizer, RunningStringSerializer, WindowSerializer
from branch.models import Advertisement, Branch, RunningString, Window
from main.services.permissions import IsBranchAdmin
from stats.models import Actions
from eqs.models import EQS
from admin_panel import serializers

from base.models import (
    DayOff,
    LanguageName,
    Service,
    Document,
    )

User = get_user_model()


class UserAdminViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserAdminSerializer
    permission_classes = [IsBranchAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.position == 'super_admin':
            queryset = User.objects.all()
        elif user.position == 'admin':
            queryset = User.objects.filter(branch=user.branch).exclude(position__in=['admin','super_admin'])
        return queryset


class QueueAdminViewSet(ModelViewSet):
    serializer_class = serializers.QueueAdminSerializer

    def get_queryset(self):
        user = self.request.user
        if user.position == 'super_admin':
            queryset = EQS.objects.all()
        elif user.position == 'admin':
            queryset = EQS.objects.filter(branch=user.branch)
        return queryset

    def get_permissions(self):
        if self.action in ['list','retrieve','update']:
            self.permission_classes = [IsBranchAdmin]
        if self.action in ['create','destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ServiceAdminViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = serializers.ServiceAdminSerializer

    def get_permissions(self):
        if self.action in ['list','retrieve']:
            self.permission_classes = [IsBranchAdmin]
        if self.action in ['create','destroy','update']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class DocumentAdminViewSet(ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = serializers.DocumentAdminSerializer

    def perform_create(self, serializer):
        lang_name_ids = self.request.data.get('lang_name', '')
        lang_name_ids_list = [int(lang_id) for lang_id in lang_name_ids.split(',') if lang_id.isdigit()]
        serializer.save(lang_name=lang_name_ids_list)

    def perform_update(self, serializer):
        lang_name_ids = self.request.data.get('lang_name', '')
        lang_name_ids_list = [int(lang_id) for lang_id in lang_name_ids.split(',') if lang_id.isdigit()]
        serializer.save(lang_name=lang_name_ids_list)

    def get_permissions(self):
        if self.action in ['list','retrieve']:
            self.permission_classes = [IsBranchAdmin]
        if self.action in ['create','destroy','update']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class BranchAdminViewSet(ModelViewSet):
    serializer_class = serializers.BranchAdminSerializer

    def get_queryset(self):
        user = self.request.user
        if user.position == 'super_admin':
            queryset = Branch.objects.all()
        elif user.position == 'admin':
            queryset = Branch.objects.filter(id=user.branch.id)
        return queryset

    def get_permissions(self):
        if self.action in ['list','retrieve','update']:
            self.permission_classes = [IsBranchAdmin]
        if self.action in ['create','destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class WindowAdminViewSet(ModelViewSet):
    serializer_class = serializers.WindowAdminSerializer

    def get_queryset(self):
        user = self.request.user
        if user.position == 'super_admin':
            queryset = Window.objects.all()
        elif user.position == 'admin':
            queryset = Window.objects.filter(branch=user.branch)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'create', 'destroy']:
            self.permission_classes = [IsBranchAdmin]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ActionsAdminViewSet(ModelViewSet):
    serializer_class = serializers.ActionsAdminSerializer

    def get_queryset(self):
        user = self.request.user
        if user.position == 'super_admin':
            queryset = Actions.objects.all()
        elif user.position == 'admin':
            queryset = Actions.objects.filter(branch=user.branch)
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'create', 'destroy']:
            self.permission_classes = [IsBranchAdmin, IsAdminUser]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class ReportAdminViewSet(ModelViewSet):
    serializer_class = serializers.ReportAdminSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'create', 'destroy']:
            self.permission_classes = [IsBranchAdmin]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.position == 'super_admin':
            queryset = Report.objects.all()
        elif user.position == 'admin':
            queryset = Report.objects.filter(branch=user.branch)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

class LanguageAdminViewSet(ModelViewSet):
    queryset = LanguageName.objects.all()
    serializer_class = serializers.LanguageAdminSerializer
    permission_classes = [IsBranchAdmin]


class DayOffAdminViewSet(ModelViewSet):
    queryset = DayOff.objects.all()
    serializer_class = serializers.DayOffAdminSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'])
    def create_multiple_dayoffs(self, request):
        day_list = request.data.get('day', [])
        created_instances = []

        for day in day_list:
            serializer = self.get_serializer(data={'day': day})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created_instances.append(serializer.data)

        return Response(created_instances)

    @action(detail=False, methods=['post'])
    def delete_multiple_dayoffs(self, request):
        days = request.data.get('days', [])
        deleted_days = []

        for day in days:
            try:
                instance = get_object_or_404(DayOff, day=day)
                self.perform_destroy(instance)
                deleted_days.append(day)
            except Http404:
                pass  

        return Response({'deleted_days': deleted_days}, status=status.HTTP_204_NO_CONTENT)


class RunningStringAdminViewSet(ModelViewSet):
    serializer_class = serializers.RunningStringAdminSerializer
    queryset = RunningString.objects.all()
    permission_classes = [IsAdminUser]

class AdvertisementAdminViewSet(ModelViewSet):
    serializer_class = AdvertisementSerilizer
    queryset = Advertisement.objects.all()
    permission_classes = [IsAdminUser]

class CreateAdvertisementView(CreateAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerilizer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AdvertisementModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerilizer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, IsAdminUser, ]

class WindowCreateAPIView(CreateAPIView):
    queryset = Window.objects.all()
    serializer_class = WindowSerializer
    permission_classes = [IsAuthenticated, IsAdminUser, ]

class CreateRunningStringView(CreateAPIView):
    queryset = RunningString.objects.all()
    serializer_class = RunningStringSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class RunningStringModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet):
    queryset = RunningString.objects.all()
    serializer_class = RunningStringSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, IsAdminUser, ]