from datetime import datetime
from dateutil.relativedelta import relativedelta
from rest_framework import serializers
from django.db.models import Count
from django.db.models.functions import TruncMonth
import calendar

from main.services import constants
from talon.models import Talon
from .models import EmployeeRating


class EmployeeRatingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EmployeeRating
        fields = '__all__'


class EmployeeRatingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeRating
        fields = ('rating', 'talon')

    def validate(self, attrs):
        rating = attrs.get('rating')
        talon = Talon.objects.filter(token=self.context['token']).first()
        
        if EmployeeRating.objects.filter(talon=talon).exists():
            raise serializers.ValidationError('You can`t patch rating')

        if not talon:
            raise serializers.ValidationError('Talon doesn`t exist.')

        if not talon.operators.exists():
            raise serializers.ValidationError('Talon wasn`t served')

        if rating not in (1, 2, 3, 4, 5):
            raise serializers.ValidationError('Wrong value! Rating must be between 1 and 5')

        attrs['talon'] = talon
        return attrs

    def create(self, validated_data):
        talon = validated_data['talon']
        rating = EmployeeRating.objects.create(**validated_data)
        rating.operators.set(talon.operators.all())
        return rating


class BranchTalonStatsSerializer(serializers.Serializer):
    start_time = serializers.DateField()
    end_time = serializers.DateField()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['month'] = self.get_talons_count()
        return rep

    def get_talons_count(self):
        start_of_month = self.validated_data.get('start_time', None)
        end_of_month = self.validated_data.get('end_time', None)

        if not start_of_month or not end_of_month:
            return []

        start_of_month = datetime(start_of_month.year, start_of_month.month, 1, 0, 0, 0)
        end_of_month = datetime(end_of_month.year, end_of_month.month, 1, 23, 59, 59) + relativedelta(day=31)

        talons_count = (
            Talon.objects
            .filter(registered_at__gte=start_of_month, registered_at__lte=end_of_month, branch=self.context['branch'])
            .annotate(month=TruncMonth('registered_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        talons_completed = (
            Talon.objects
            .filter(registered_at__gte=start_of_month, registered_at__lte=end_of_month, branch=self.context['branch'], status=constants.TALON_STATUS_COMPLETED)
            .annotate(month=TruncMonth('registered_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        talons_canceled = (
            Talon.objects
            .filter(registered_at__gte=start_of_month, registered_at__lte=end_of_month, branch=self.context['branch'], status=constants.TALON_STATUS_CANCELED)
            .annotate(month=TruncMonth('registered_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        result = []

        for month_num in range(start_of_month.month, end_of_month.month + 1):
            month_name = calendar.month_name[month_num]

            count = next((item['count'] for item in talons_count if item['month'].month == month_num), 0)
            completed = next((item['count'] for item in talons_completed if item['month'].month == month_num), 0)
            canceled = next((item['count'] for item in talons_canceled if item['month'].month == month_num), 0)

            month_data = {
                'month': month_name,
                'talon_count': count,
                'talon_completed': completed,
                'talon_canceled': canceled,
            }

            result.append(month_data)

        return result


