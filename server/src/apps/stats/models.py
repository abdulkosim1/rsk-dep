from django.db import models
from django.contrib.auth import get_user_model
from apps.branch.models import Branch

from apps.talon.models import Talon

User = get_user_model()


class EmployeeRating(models.Model):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    RATING_CHOICES = (
        (ONE, '1'),
        (TWO, '2'),
        (THREE, '3'),
        (FOUR, '4'),
        (FIVE, '5')
    )
    talon = models.ForeignKey(
        to=Talon,
        on_delete=models.CASCADE,
        related_name='ratings',
        blank=True
    )
    operators = models.ManyToManyField(
        to=User,
        related_name='ratings',
        blank=True
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, 
        blank=True, 
        null=True)


    def __str__(self):
        return str(self.rating)


class Actions(models.Model):
    employee = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name="actions",
        verbose_name="Employee",
        blank=True,
        null=True,
    )
    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.SET_NULL,
        related_name="actions",
        verbose_name="Branch",
        blank=True,
        null=True,
    )
    action = models.CharField(max_length=200)
    registerd_time = models.DateTimeField(auto_now_add=True)

