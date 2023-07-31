from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.db import models


class ClientManager(BaseUserManager):
    def _create(self, phone, password, **extra_fields):
        user = self.model(
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, phone, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', False)
        return self._create(phone, password, **extra_fields)


class Client(AbstractBaseUser):
    phone = models.CharField(max_length=13, unique=True)
    code = models.CharField(max_length=8, blank=True)

    registration_date = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = ClientManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['phone']

    def __str__(self) -> str:
        return f"{self.phone}"


    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, obj=None):
        return self.is_staff

    def save(self, *args, **kwargs):
        if not self.phone:
            raise ValidationError('Поле номера не может быть пустым!')
        super().save(*args, **kwargs)

    def create_code(self):
        code = get_random_string(length=8)
        if Client.objects.filter(code=code).exists():
            self.create_code()
        self.code = code
        self.save()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class CustomToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    client = models.OneToOneField(Client, related_name='custom_token', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.key