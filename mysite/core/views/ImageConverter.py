from .imports import *
import random
from django.core.files.base import ContentFile
import string

class ImageConverter(generics.ListCreateAPIView):
    queryset = ImageConverterModel.objects.all()
    serializer_class = ImageConverterSerializer

    def post(self, request, *args, **kwargs):
        serializer = ImageConverterSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            original_image = instance.original_image
            image_name = os.path.splitext(os.path.basename(original_image.name))[0]
            image_extension = os.path.splitext(original_image.name)[1].lower()
            convert_to = serializer.validated_data['convert_to']
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

            # Define allowed formats
            formats_allowed = ['.png', '.gif', '.webp', '.tiff', '.bmp', '.jpg']
            if image_extension not in formats_allowed:
                return Response({"error": "Unsupported image format."}, status=status.HTTP_400_BAD_REQUEST)

            if convert_to not in formats_allowed:
                return Response({"error": "Unsupported conversion format."}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new name for the converted image based on the selected format
            converted_image_name = f"{image_name}_{random_string}_Converted_To_{convert_to[1:].upper()}{convert_to}"
            
            # Open the image and convert to the chosen format
            image = Image.open(original_image)
            img_content = ContentFile(b'')
            
            if convert_to == '.jpg':
                rgb_image = image.convert('RGB')  # Convert to RGB for JPEG compatibility
                rgb_image.save(img_content, format='JPEG')
            else:
                image.save(img_content, format=convert_to[1:].upper())

            # Save the ContentFile to the converted_image field in the instance
            instance.converted_image.save(converted_image_name, img_content, save=True)

            # Ensure the correct URLs are returned in the response
            original_image_url = request.build_absolute_uri(instance.original_image.url)
            converted_image_url = request.build_absolute_uri(instance.converted_image.url)

            return Response({
                "id": instance.id,
                "original_image": original_image_url,
                "converted_image": converted_image_url
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        # Delete all instances and their associated images
        instances = ImageConverterModel.objects.all()
        for instance in instances:
            instance.original_image.delete(save=False)  # Delete original image file
            instance.converted_image.delete(save=False)  # Delete converted image file
            instance.delete()  # Delete model instance

        return Response({"message": "images deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class RetrieveDestroyImage(generics.RetrieveDestroyAPIView):
    queryset=ImageConverterModel.objects.all()
    serializer_class=ImageConverterSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the object instance

        # Delete the original and converted images if they exist
        if instance.original_image:
            instance.original_image.delete(save=False)
        if instance.converted_image:
            instance.converted_image.delete(save=False)

        # Now delete the instance from the database
        instance.delete()

        return Response({"message": "All images deleted successfully."},status=status.HTTP_204_NO_CONTENT)
