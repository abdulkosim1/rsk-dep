from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .models import CustomToken
from rest_framework import serializers

from .tasks import send_sms_code
from services.utils import normalize_phone
from . models import Client


def phone_validator(phone):
    phone = normalize_phone(phone)
    if not Client.objects.filter(phone=phone).exists():
        raise serializers.ValidationError(
            'User with this email does not exist'
        )
    return phone


class RegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(required=True)

    class Meta:
        model = Client
        fields = ('phone', 'password', 'password_confirm')

    def validate_phone(self, phone):
        phone = normalize_phone(phone)
        if len(phone) != 13:
            raise serializers.ValidationError('Неверный формат телефона')
        if Client.objects.filter(phone=phone).exists():
            raise serializers.ValidationError('Этот номер уже зарегестрирован')
        return phone
    
    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают!')
        return attrs

    def create(self, validated_data):
        user = Client.objects.create_user(**validated_data)
        user.create_code()
        send_sms_code(
            phone=user.phone,
            code=user.code,
            body='Это Ваш активационный код'
            )
        return user


class ActivationSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=13, required=True)
    code = serializers.CharField(max_length=10, required=True)

    def validate_phone(self, phone):
        phone = normalize_phone(phone)
        if len(phone) != 13:
            raise serializers.ValidationError('Неверный формат телефона')
        if not Client.objects.filter(phone=phone).exists():
            raise serializers.ValidationError('Пользователь с таким номером телефона не найден')
        return phone

    def validate_code(self, code):
        if not Client.objects.filter(code=code).exists():
            raise serializers.ValidationError('Неверный код')
        return code

    def activate_account(self):
        phone = self.validated_data.get('phone')
        user = Client.objects.get(phone=phone)
        user.is_active = True
        user.code = ''
        user.save()


class RestorePasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(
        required=True, 
        max_length=13, 
        validators=[phone_validator]
        )

    def send_code(self):
        phone = self.validated_data.get('phone')
        user = Client.objects.get(phone=phone)
        user.create_code()
        send_sms_code(
            phone=user.phone,
            code=user.code,
            body='Это Ваш код восстановления'
            )


class SetRestoredPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(
        required=True, 
        max_length=13, 
        validators=[phone_validator]
        )
    code = serializers.CharField(min_length=1, max_length=8, required=True)
    new_password = serializers.CharField(max_length=128, required=True)
    new_pass_confirm = serializers.CharField(max_length=128, required=True)

    def validate_code(self, code):
        if not Client.objects.filter(code=code).exists():
            raise serializers.ValidationError(
                'Wrong code'
            )
        return code

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_pass_confirm = attrs.get('new_pass_confirm')
        if new_password != new_pass_confirm:
            raise serializers.ValidationError(
                'Passwords do not match'
            )
        return attrs
        
    def set_new_password(self):
        phone = self.validated_data.get('phobe')
        user = Client.objects.get(phone=phone)
        new_password = self.validated_data.get('new_password')
        user.set_password(new_password)
        user.code = ''
        user.save()


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        try:
            custom_token = CustomToken.objects.get(key=refresh)
        except CustomToken.DoesNotExist:
            raise serializers.ValidationError('Invalid token.')

        access_token = custom_token.client.get_access_token()

        # Add the new access token to the response data
        data['access'] = str(access_token)

        return data