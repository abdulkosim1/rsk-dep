from rest_framework import serializers
from django.utils.timezone import timedelta
import qrcode
import base64
from io import BytesIO

from main.services import constants
from .models import Talon
from branch.serializers import BranchSerializer
from base.models import DayOff
from client.models import Client


class TalonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talon
        exclude = ['operators','service','branch']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['service'] = instance.service.name
        rep['branch'] = BranchSerializer(instance.branch).data

        if not instance.is_appointed:
            earlier_talons = Talon.objects.filter(
                appointment_date__date=instance.appointment_date.date(),
                appointment_date__lt=instance.appointment_date
            )

            position_in_queue = earlier_talons.count() + 1
            rep['position_in_queue'] = position_in_queue
        return rep


class TalonCreateSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Talon
        exclude = ['operators']

    def get_qr_code(self, instance):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(instance.token)
        qr.make(fit=True)

        qr_image_stream = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(qr_image_stream, "PNG")
        qr_image_stream.seek(0)

        qr_code_image_base64 = base64.b64encode(qr_image_stream.getvalue()).decode('utf-8')
        return qr_code_image_base64

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['branch'] = BranchSerializer(instance.branch).data
        talons_count = Talon.objects.filter(
                service=instance.service, 
                branch=instance.branch,
                appointment_date__date=instance.appointment_date.date(),
                status__in=[constants.TALON_STATUS_WAITING, 
                    constants.TALON_STATUS_INSERVICE]
                ).count()
        rep['talons_in_queue'] = talons_count
        
        earlier_talons = Talon.objects.filter(
            appointment_date__date=instance.appointment_date.date(),
            appointment_date__lt=instance.appointment_date
        )

        position_in_queue = earlier_talons.count() + 1
        rep['position_in_queue'] = position_in_queue
        rep['estimated_time_in_min'] = talons_count*instance.service.average_time
        rep['service_name'] = instance.service.name
        return rep

    def validate(self, attrs):
        appointment_date = attrs.get('appointment_date')

        if appointment_date:
            day = appointment_date.date()

            if DayOff.objects.filter(day=day).exists():
                raise serializers.ValidationError('Appointment date is a day off')

            talon_start = appointment_date - timedelta(minutes=attrs['service'].average_time)
            talon_end = appointment_date + timedelta(minutes=attrs['service'].average_time)

            if Talon.objects.filter(
                branch=attrs['branch'],
                service=attrs['service'],
                appointment_date__range=(talon_start, talon_end),
                status=constants.TALON_STATUS_WAITING
            ).exists():
                raise serializers.ValidationError('Talon already exists')

        return attrs

    def create(self, validated_data):
        talon = Talon.objects.create(**validated_data)
        if isinstance(self.context['request'].user, Client):
            talon.client = self.context['request'].user
        talon.save()
        return talon



class TerminalTalonCreateSerializer(serializers.ModelSerializer):
    qr_code = serializers.SerializerMethodField()

    class Meta:
        model = Talon
        exclude = ['operators']

    def get_qr_code(self, instance):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(instance.token)
        qr.make(fit=True)

        qr_image_stream = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(qr_image_stream, "PNG")
        qr_image_stream.seek(0)

        qr_code_image_base64 = base64.b64encode(qr_image_stream.getvalue()).decode('utf-8')
        return qr_code_image_base64

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['branch'] = BranchSerializer(instance.branch).data
        talons_count = Talon.objects.filter(
                service=instance.service, 
                branch=instance.branch,
                appointment_date__date=instance.appointment_date.date(),
                status__in=[constants.TALON_STATUS_WAITING, 
                    constants.TALON_STATUS_INSERVICE]
                ).count()
        rep['talons_in_queue'] = talons_count
        
        earlier_talons = Talon.objects.filter(
            appointment_date__date=instance.appointment_date.date(),
            appointment_date__lt=instance.appointment_date
        )

        position_in_queue = earlier_talons.count() + 1
        rep['position_in_queue'] = position_in_queue
        rep['estimated_time_in_min'] = talons_count*instance.service.average_time
        rep['service_name'] = instance.service.name
        return rep

    def validate(self, attrs):
        appointment_date = attrs.get('appointment_date')

        if appointment_date:
            day = appointment_date.date()

            if DayOff.objects.filter(day=day).exists():
                raise serializers.ValidationError('Appointment date is a day off')

            talon_start = appointment_date - timedelta(minutes=attrs['service'].average_time)
            talon_end = appointment_date + timedelta(minutes=attrs['service'].average_time)

            if Talon.objects.filter(
                branch=attrs['branch'],
                service=attrs['service'],
                appointment_date__range=(talon_start, talon_end),
                status=constants.TALON_STATUS_WAITING
            ).exists():
                raise serializers.ValidationError('Talon already exists')

        return attrs

    def create(self, validated_data):
        talon = Talon.objects.create(**validated_data)
        talon.save()
        return talon