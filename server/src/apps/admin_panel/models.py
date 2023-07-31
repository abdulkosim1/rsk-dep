from django.db import models
from django.contrib.auth import get_user_model
from apps.branch.models import Branch

from services.validations import validate_excel_extension, validate_pdf_extension

User = get_user_model()


class Report(models.Model):
    pdf_file = models.FileField()
    exel_file = models.FileField()
    
    registration_date = models.DateTimeField(auto_now_add=True)

    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.CASCADE,
        related_name='report',
        verbose_name='Филиал',
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='report',
        verbose_name='админ',
        blank=True,
        null=True
    )

    def __str__(self) -> str:
        return f'отчет по филиалу {self.branch}'