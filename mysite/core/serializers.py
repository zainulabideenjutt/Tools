from rest_framework import serializers
from .models import ConverterModel
from .models import ImageConverterModel,PdfToImageModel,ImagesToPdf
class ConverterSerializer(serializers.ModelSerializer):
        class Meta:
            model = ConverterModel
            fields = "__all__"
class ImageConverterSerializer(serializers.ModelSerializer):
    class Meta:
        model =ImageConverterModel
        fields='__all__'
class PdfToImageSerializer(serializers.ModelSerializer):
    class Meta:
        model =PdfToImageModel
        fields='__all__'
class ImagesToPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model =ImagesToPdf
        fields='__all__'
class PdfToOnlyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model =PdfToImageModel
        fields=['id','Image']