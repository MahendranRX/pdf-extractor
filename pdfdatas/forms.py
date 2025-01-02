from django import forms
from .models import *


class PdfFileForm(forms.ModelForm):
    class Meta:
        model = PdfFiles
        fields = ['file']


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'designation', 'salary']
