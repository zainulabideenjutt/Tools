from rest_framework import serializers
from .models import ConverterModel
from .models import ImageConverterModel
class ConverterSerializer(serializers.ModelSerializer):
        class Meta:
            model = ConverterModel
            fields = "__all__"
class ImageConverterSerializer(serializers.ModelSerializer):
    class Meta:
        model =ImageConverterModel
        fields='__all__'