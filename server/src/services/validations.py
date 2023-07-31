from django.core.exceptions import ValidationError
import os

def validate_pdf_extension(value):
    ext = os.path.splitext(value.name)[1]  
    valid_extensions = ['.pdf']  

    if not ext.lower() in valid_extensions:
        raise ValidationError('Неверный формат файла PDF. Допустимый формат: .pdf')

def validate_excel_extension(value):
    ext = os.path.splitext(value.name)[1]  
    valid_extensions = ['.xls', '.xlsx']  

    if not ext.lower() in valid_extensions:
        raise ValidationError('Неверный формат файла Excel. Допустимые форматы: .xls, .xlsx')
