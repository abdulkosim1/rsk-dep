from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.shortcuts import get_object_or_404

from . serializers import EQSSerializer, QueueSerializer
from . models import EQS


class EQSListView(APIView):

    def get(self, request:Request):
        terminals = EQS.objects.all()
        serializer = EQSSerializer(terminals, many=True)
        return Response(serializer.data)


class EQSRetrieveView(APIView):

    def get(self, request:Request,pk:int):
        queue = get_object_or_404(EQS, id=pk)
        serializer = QueueSerializer(queue)
        return Response(serializer.data)


