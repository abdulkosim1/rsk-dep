from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db.models import Avg
from datetime import datetime

from apps.base.models import Service, Document, LanguageName, DayOff
from apps.branch.models import Advertisement, RunningString, Window, Branch
from apps.admin_panel.models import Report
from apps.stats.models import Actions
from apps.eqs.models import EQS

User = get_user_model()

class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['is_staff']

    def validate_email(self, email):
        if self.instance is None and User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already in use')
        return email

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rating = instance.ratings.aggregate(Avg('rating'))['rating__avg']
        if rating:
            rep['rating'] = round(rating, 1)
        else:
            rep['rating'] = 0.0
        return rep

    def create(self, validated_data):
        services_data = validated_data.pop('service', [])  

        user = User.objects.create_user(**validated_data)

        for service_data in services_data:
            user.service.add(service_data)

        return user


class ActionsAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actions
        fields = '__all__'

class QueueAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = EQS
        fields = '__all__'


class ServiceAdminSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Service
        fields = '__all__'

class CustomDateField(serializers.DateField):
    def to_internal_value(self, value):
        if isinstance(value, list):
            return [self.parse_date(date_str) for date_str in value]
        else:
            return self.parse_date(value)

    def parse_date(self, date_str):
        try:
            if isinstance(date_str, str):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                return date_obj
            else:
                return date_str
        except ValueError:
            raise serializers.ValidationError("Неправильный формат date. Используйте один из этих форматов: YYYY-MM-DD.")

class DayOffAdminSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DayOff
        fields = '__all__'


class DocumentAdminSerializer(serializers.ModelSerializer):
    lang_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = '__all__'

    def get_lang_name(self, obj):
        return list(obj.lang_name.values_list('id', flat=True))

    def create(self, validated_data):
        lang_name_ids = validated_data.pop('lang_name', [])
        document = super().create(validated_data)
        document.lang_name.set(lang_name_ids)
        return document

    def update(self, instance, validated_data):
        lang_name_ids = validated_data.pop('lang_name', [])
        document = super().update(instance, validated_data)
        document.lang_name.set(lang_name_ids)
        return document


class WindowAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Window
        fields = '__all__'


class BranchAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Branch
        fields = '__all__'


class LanguageAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = LanguageName
        fields = '__all__'


class ReportAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        exclude = ('user','branch')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['author'] = instance.user.username
        rep['branch'] = BranchAdminSerializer(instance.user.branch).data
        return rep

    def create(self, validated_data):
        user = self.context.get('user')
        report = Report.objects.create(user=user, branch=user.branch, **validated_data)
        return report


class AdvertisementAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Advertisement
        fields = '__all__'


class RunningStringAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = RunningString
        fields = '__all__'
