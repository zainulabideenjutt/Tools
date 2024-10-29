from rest_framework import serializers
from .models import ConverterModel
from .models import ImageConverterModel,ImagesToPdf,PdfToImagesModel
class ConverterSerializer(serializers.ModelSerializer):
        class Meta:
            model = ConverterModel
            fields = "__all__"
class ImageConverterSerializer(serializers.ModelSerializer):
    convert_to = serializers.ChoiceField(
        choices=[
            ('.jpg', 'JPEG'),
            ('.png', 'PNG'),
            ('.gif', 'GIF'),
            ('.webp', 'WEBP'),
            ('.tiff', 'TIFF'),
            ('.bmp', 'BMP')
        ],required=False,
        help_text="Choose the format to convert the image to."
    )

    class Meta:
        model = ImageConverterModel
        fields = ['id','original_image', 'convert_to', 'converted_image']
        read_only_fields = ['converted_image']

    def create(self, validated_data):
        convert_to = validated_data.pop('convert_to')  # Remove convert_to from validated_data
        instance = super().create(validated_data)  # Create the model instance without convert_to
        # Handle any conversion logic here if necessary
        return instance
class PdfToImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PdfToImagesModel
        fields = ['document', 'converted_images']
        read_only_fields = ['converted_images']
class ImagesToPdfSerializer(serializers.ModelSerializer):
    class Meta:
        model =ImagesToPdf
        fields='__all__'
# class PdfToOnlyImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model =PdfToImageModel
#         fields=['id','Image']