from rest_framework import serializers

from . models import EQS
from apps.talon.models import Talon
from apps.base.serializers import DocumentSerializer


class EQSSerializer(serializers.ModelSerializer):

    class Meta:
        model = EQS
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep


class QueueTalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talon
        fields = ['token','status']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['service'] = instance.service.name
        return rep


class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EQS
        fields = '__all__'

    def get_queue(self, branch, service):
        talons = QueueTalonSerializer(Talon.objects.filter(branch=branch, service=service).all(), many=True).data
        queue = [{ "token": talon['token'], "status": talon['status'], "service": talon['service'] } for talon in talons]
        return queue

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['queue'] = self.get_queue(instance.branch, instance.service)
        return rep

