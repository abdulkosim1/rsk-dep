from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import date, timedelta
from django.db.models import Avg

from main.services import constants
from base.serializers import ServiceSerializer
from talon.models import Talon

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password','id','last_login','is_staff']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['service'] = ServiceSerializer(instance.service.all(), many=True).data
        rating = instance.ratings.aggregate(Avg('rating'))['rating__avg']
        if rating:
            rep['rating'] = round(rating, 1)
        else:
            rep['rating'] = 0.0
        return rep

    


class OperatorQueueTalonsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Talon
        fields = ['token','status','client_type','registered_at','appointment_date','service_start','service_end']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['service'] = instance.service.name
        return rep


class OperatorQueueSerializer(serializers.Serializer):
    clients_per_day = serializers.SerializerMethodField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['talons'] = OperatorQueueTalonsSerializer(instance,many=True).data
        return rep

    def get_clients_per_day(self, obj):
        today = date.today()
        yesterday = today - timedelta(days=1)
        request = self.context.get('request')
        operator = request.user
        clients_complete_today = Talon.objects.filter(service_end__date=today, operators=operator, status=constants.TALON_STATUS_COMPLETED).count()
        clients_complete_yesterday = Talon.objects.filter(service_end__date=yesterday, operators=operator, status=constants.TALON_STATUS_COMPLETED).count()
        clients_canceled_today = Talon.objects.filter(service_end__date=today, operators=operator, status=constants.TALON_STATUS_CANCELED).count()
        clients_canceled_yesterday = Talon.objects.filter(service_end__date=yesterday, operators=operator, status=constants.TALON_STATUS_CANCELED).count()
        return {
            'today': {
                'completed': clients_complete_today,
                'canceled': clients_canceled_today
            },
            'yesterday': {
                'completed': clients_complete_yesterday,
                'canceled': clients_canceled_yesterday
            }
        }

 
class RegistratorQueueSerializer(serializers.Serializer):
    clients_per_day = serializers.SerializerMethodField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['talons'] = OperatorQueueTalonsSerializer(instance,many=True).data
        return rep

    def get_clients_per_day(self, obj):
        today = date.today()
        yesterday = today - timedelta(days=1)
        request = self.context.get('request')
        branch = request.user.branch
        clients_complete_today = Talon.objects.filter(service_end__date=today, branch=branch, status=constants.TALON_STATUS_COMPLETED).count()
        clients_complete_yesterday = Talon.objects.filter(service_end__date=yesterday, branch=branch, status=constants.TALON_STATUS_COMPLETED).count()
        clients_canceled_today = Talon.objects.filter(service_end__date=today, branch=branch, status=constants.TALON_STATUS_CANCELED).count()
        clients_canceled_yesterday = Talon.objects.filter(service_end__date=yesterday, branch=branch, status=constants.TALON_STATUS_CANCELED).count()
        return {
            'today': {
                'completed': clients_complete_today,
                'canceled': clients_canceled_today
            },
            'yesterday': {
                'completed': clients_complete_yesterday,
                'canceled': clients_canceled_yesterday
            }
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        user = self.user
        data['position'] = user.position
        
        return data