from django.db import models
from django.core.validators import FileExtensionValidator

# Create your models here.


class PdfFiles(models.Model):
    file = models.FileField(upload_to='pdffiles',
                            validators=[FileExtensionValidator(allowed_extensions=['pdf'])])

    class Meta:
        unique_together = ('file',)

    def __str__(self):
        return self.file.name


class Employee(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    salary = models.FloatField(null=True)

    def __str__(self):
        return self.name
