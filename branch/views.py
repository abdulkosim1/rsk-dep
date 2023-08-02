from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import mixins
from apps.base.serializers import ServiceSerializer

from services import constants
from services.permissions import IsOperator
from apps.eqs.serializers import EQSSerializer
from apps.talon.models import Monitor, Talon
from apps.eqs.models import EQS

from .models import Branch, RunningString, Advertisement, Window
from .serializers import (BranchSerializer, 
    BranchQueueSerializer, 
    RunningStringSerializer, 
    AdvertisementSerilizer, 
    WindowSerializer, 
    MonitorSerializer
    )


class BranchListView(APIView):

    def get(self, request: Request):
        branches = Branch.objects.all()
        serializer = BranchSerializer(branches, many=True)
        return Response(serializer.data)

class BranchRetrieveView(APIView):
    def get(self, request: Request, pk: int):
        branch = Branch.objects.get(pk=pk)
        serializer = BranchSerializer(branch)
        return Response(serializer.data)

class BranchQueueView(APIView):
    def get(self, request: Request, pk: int):
        queues = EQS.objects.filter(branch=pk)
        serializer = EQSSerializer(queues, many=True)
        return Response({'queues': serializer.data})

class BranchMainQueueView(APIView):
    def get(self, request: Request, branch_id: int):
        queue = Talon.objects.filter(branch=branch_id, status__in=[constants.TALON_STATUS_WAITING, constants.TALON_STATUS_INSERVICE])
        serializer = BranchQueueSerializer(queue, many=True)
        return Response(serializer.data)

class BranchServiceView(APIView):

    def get(self, request: Request, pk: int):
        branch = Branch.objects.filter(id=pk).first()
        res = ServiceSerializer(branch.service, many=True).data
        return Response(res)

class GetRunningStringView(APIView):
    def get(self, request: Request):
        strings = RunningString.objects.all()
        serializer = RunningStringSerializer(strings, many=True)
        return Response(serializer.data)

class WindowView(APIView): # fixed bugs
    def get(self, request: Request, branch_id: int):
        queue = Talon.objects.filter(branch=branch_id, status__in=[constants.TALON_STATUS_WAITING, constants.TALON_STATUS_INSERVICE])
        serializer = BranchQueueSerializer(queue,  many=True)
        return Response(serializer.data)

class AdvertisementView(APIView):
    def get(self, request):
        queryset = Advertisement.objects.all()
        serializer = AdvertisementSerilizer(queryset, many=True)
        return Response(serializer.data)

class WindowListAPIView(ListAPIView):
    queryset = Window.objects.all()
    serializer_class = WindowSerializer

    def get_queryset(self):
        queryset = Window.objects.filter(branch_id=self.kwargs["pk"])
        return queryset


class MonitorList(APIView):
    def get(self, request: Request, branch_id: int):
        queue = Monitor.objects.filter(branch=branch_id)
        serializer = MonitorSerializer(queue, many=True)
        return Response(serializer.data)

class MonitorAPIUpdate(mixins.UpdateModelMixin,
    GenericViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    permission_classes = [IsAuthenticated, IsOperator]
    