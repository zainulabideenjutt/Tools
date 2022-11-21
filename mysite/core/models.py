from django.db import models

# Create your models here.
class WordToPDFModel(models.Model):
    file=models.FileField()
    pdfFile=models.TextField(null=True,blank=True,default="")
