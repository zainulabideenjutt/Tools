from django.db import models

# Create your models here.
class ConverterModel(models.Model):
    file=models.FileField()
    ConvertedFile=models.TextField(null=True,blank=True,default="")
    
class ImageConverterModel(models.Model):
    image=models.ImageField()
    convertedImage=models.TextField(null=True,blank=True,default="")
    
