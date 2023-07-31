from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError

from apps.base.models import Service
from apps.branch.models import Branch, Window


class UserManager(BaseUserManager):
    def _create(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('User must have first name')
        if not email:
            raise ValueError('User must have email')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        return self._create(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('position', 'super_admin')
        return self._create(username, email, password, **extra_fields)


class User(AbstractBaseUser):
    super_admin = 'super_admin'
    admin = 'admin'
    operator = 'operator'
    registrator = 'registrator'
    POSITION_CHOICES = (
        (super_admin, 'super_admin'),
        (admin, 'admin'),
        (operator, 'operator'),
        (registrator, 'registrator'),
    )
    email = models.EmailField('Эл. Почта', max_length=255, unique=True)

    # image = models.ImageField(blank=True, )

    username = models.CharField('ФИО', max_length=255)
    position = models.CharField(choices=POSITION_CHOICES,max_length=100)
    shift = models.CharField('Перерыв', max_length=100, blank=True)
    comment = models.CharField('Коментарий', max_length=100, blank=True)
    status = models.CharField('Статус', max_length=255, default='active')

    max_transport = models.PositiveIntegerField('Ограничение переноса талонов',default=0)

    auto_call = models.BooleanField('Авто вызов талона',default=False)
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    registration_date = models.DateTimeField(auto_now_add=True)

    window = models.OneToOneField(
        to=Window,
        on_delete=models.CASCADE,
        related_name='employee',
        verbose_name='Окно',
        null=True,
        blank=True,
    )
    service = models.ManyToManyField(
        to=Service,
        related_name='employee',
        verbose_name='Услуги',
        blank=True,
    )
    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.CASCADE,
        related_name='employee',
        verbose_name='Филиал',
        null=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return f"{self.username}"

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, obj=None):
        return self.is_staff

    def save(self,*args, **kwargs):
        if not self.username:
            raise ValidationError('Поле имени не может быть пустым!')
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'