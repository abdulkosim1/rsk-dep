from rest_framework import serializers

from apps.base.serializers import LanguageSerializer

from .models import Branch, RunningString, Advertisement, Window
from apps.talon.models import Talon, Monitor


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['lang_name'] = LanguageSerializer(instance.lang_name.all(), many=True).data
        return rep

class BranchQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talon
        fields = ['token', 'status']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['service'] = instance.service.name
        latest_window = instance.operators.last().window if instance.operators.exists() else None
        rep['window'] = latest_window
        return rep


class RunningStringSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunningString
        fields = '__all__'

class AdvertisementSerilizer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'

class WindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Window
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['status'] = instance.employee.status
        return rep

class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['talon'] = instance.talon.token
        return rep