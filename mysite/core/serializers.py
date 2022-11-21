from rest_framework import serializers
from .models import WordToPDFModel
class WordToPDFSerializer(serializers.ModelSerializer):
        class Meta:
            model = WordToPDFModel
            fields = "__all__"
