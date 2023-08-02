from rest_framework import serializers

from . models import Terminal, Document, Service, LanguageName, DayOff


class TerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['lang_name'] = LanguageSerializer(instance.lang_name.all(), many=True).data
        return rep


class TerminalAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField(max_length=200, required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not Terminal.objects.filter(auth_token=attrs.get('auth_token')).exists():
            raise serializers.ValidationError('Not Authenticated')
        return attrs


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageName
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id','name','lang_name')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['lang_name'] = LanguageSerializer(instance.lang_name.all(), many=True).data
        rep['documents'] = DocumentSerializer(instance.documents.all(), many=True).data
        return rep


