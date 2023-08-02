from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from main.services.permissions import IsBranchAdmin
from . serializer import EmployeeRatingSerializer, EmployeeRatingCreateSerializer, BranchTalonStatsSerializer
from . models import EmployeeRating

class SetRatingView(APIView):

    def get(self, request:Request):
        rating = EmployeeRating.objects.all()
        serializer = EmployeeRatingSerializer(rating, many=True)
        return Response(serializer.data)

    def post(self, request:Request):
        serializer = EmployeeRatingCreateSerializer(data=request.data,context={'token': request.data['token']})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


class BranchTalonStatsView(APIView):
    permission_classes=[IsBranchAdmin,IsAuthenticated]

    def post(self, request):
        serializer = BranchTalonStatsSerializer(data=request.data, context={'branch': request.user.branch})
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data)
