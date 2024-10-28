from .imports import *
import random
from django.core.files.base import ContentFile
import string

class ImageConverter(generics.ListCreateAPIView, generics.DestroyAPIView):
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

        return Response({"message": "All images deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class RetriveSingleImage(generics.RetrieveUpdateDestroyAPIView):
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

# class ImageConverter(generics.ListCreateAPIView,generics.RetrieveAPIView):
#     queryset=ImageConverterModel.objects.all()
#     formats_allowed=['.png', '.gif', '.webp', '.tiff', '.bmp','.jpg']
#     serializer_class=ImageConverterSerializer
#     def generate_random_string(self,string_length=6):
#         """Returns a random string of length string_length."""
#         random = str(uuid.uuid4()) # Convert UUID format to a Python string.
#         random = random.upper() # Make all characters uppercase.
#         random = random.replace("-","") # Remove the UUID '-'.
#         return random[0:string_length] # Return the random string.
#     def return_response(self,**data):
#             serializer = self.get_serializer(data=data['data'])
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             headers = self.get_success_headers(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#     # def get(self,request,*args,**kwargs):
#     #     pk=kwargs.get('pk')
#     #     if pk is not None:
#     #         return self.retrieve(request,*args,**kwargs)
#         # return self.list(request,*args,**kwargs)
#     def post(self, request, *args, **kwargs):
#         serializer = ImageConverterSerializer(data=request.data)
#         if serializer.is_valid():
#             instance = serializer.save()
#             original_image = instance.original_image
#             image_name = os.path.splitext(os.path.basename(original_image.name))[0]
#             image_extension = os.path.splitext(original_image.name)[1].lower()
#             convert_to = serializer.validated_data['convert_to']  # Get the chosen output format
#             random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            
#             # Define allowed formats
#             formats_allowed = ['.png', '.gif', '.webp', '.tiff', '.bmp', '.jpg']
            
#             # Check if the original image format is allowed
#             if image_extension not in formats_allowed:
#                 return Response({"error": "Unsupported image format. Allowed formats are: " + ", ".join(formats_allowed)}, status=400)

#             # Check if the conversion format is valid
#             if convert_to not in formats_allowed:
#                 return Response({"error": "Unsupported conversion format. Allowed formats are: " + ", ".join(formats_allowed)}, status=400)

#             # Create a new name for the converted image based on the selected format
#             converted_image_name = f"{image_name}_{random_string}_Converted_To_{convert_to[1:].upper()}{convert_to}"
            
#             # Open the image and convert to the chosen format
#             image = Image.open(original_image)
#             if convert_to == '.jpg':
#                 rgb_image = image.convert('RGB')  # Convert to RGB for JPEG compatibility
#                 img_content = ContentFile(b'')
#                 rgb_image.save(img_content, format='JPEG')
#             else:
#                 img_content = ContentFile(b'')
#                 image.save(img_content, format=convert_to[1:].upper())  # Save in the selected format
            
#             # Save the ContentFile to the converted_image field in the instance
#             instance.converted_image.save(converted_image_name, img_content, save=True)

#             # Ensure the correct URLs are returned in the response
#             original_image_url = request.build_absolute_uri(instance.original_image.url)
#             converted_image_url = request.build_absolute_uri(instance.converted_image.url)

#             return Response({
#                 "original_image": original_image_url,
#                 "converted_image": converted_image_url
#             })

#         return Response(serializer.errors, status=400)


#         print(image_name)
#         inComingImageFile=request.data.get('original_image')
#         if inComingImageFile is not None:
#             imageName=inComingImageFile.name
#             imageExtension=imageName[imageName.rindex('.'):]
#             image=Image.open(inComingImageFile)
#         else:
#             return Response({'detail':'please provide a image you want to convert.'})

#         randomString=f"{str(datetime.datetime.now().time()).replace('.','').replace(':','')}"
#         basePath=Path(__file__).resolve().parent.parent.parent
#         ImageSavingLocation=f"{basePath}\\media\\"
#         return Response({})
#         # convertTo=request.data.get('convert_to')
#         # inComingPurpose=request.data.get('purpose')
#         if  imageExtension=='.png':
#             randomImageName=f"{imageName[:imageName.rindex('.')]}_{randomString}_Converted_From_{imageExtension[1:].upper()}_To_{convertTo[1:].upper()}{convertTo}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}",format='png')
#             # save to database
#             return Response({})
#         if inComingPurpose is not None:
#             if  inComingPurpose=='resize' and inComingImageFile:
#                 randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#                 width=request.data['width']
#                 height=request.data['height']
#                 RGBImage=image.resize((width,height))
#                 RGBImage.save(f"{ImageSavingLocation}{randomImageName}{imageExtension}")
#                 domain=request.get_host()
#                 storagePathFromDomain=f"http://{domain}/media/"
#                 data={'convertedFromExtension':imageExtension,
#                     'convertedImage':f'{storagePathFromDomain}{randomImageName}{imageExtension}',  
#                     }
#                 return self.return_response(data=data)
#             if inComingPurpose=='crop' and inComingImageFile :
#                 randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#                 # RGBImage=image.convert('RGB')
#                 width, height = image.size
#                 if request.data['x_axis'] and request.data['y_axis'] and request.data['width'] and request.data['height']:
#                     x_axis = request.data['x_axis']
#                     y_axis = request.data['y_axis']
#                     xPlusWidth = request.data['width']+x_axis
#                     yPlusHeight = request.data['height']+y_axis
#                     if x_axis < width and y_axis<height and  xPlusWidth>width-x_axis and yPlusHeight>height-y_axis :
#                         RGBImage=image.crop((x_axis,y_axis,xPlusWidth,yPlusHeight))
#                         RGBImage.save(f"{ImageSavingLocation}{randomImageName}{imageExtension}")
#                         domain=request.get_host()
#                         storagePathFromDomain=f"http://{domain}/media/"
#                         data={'convertedFromExtension':imageExtension,
#                             'convertedImage':f'{storagePathFromDomain}{randomImageName}{imageExtension}',  
#                             }
#                         return self.return_response(data=data)
#                 else:
#                     return Response({'detail':'something went wrong with coordinates'})

#         if convertTo=='.png' and imageExtension=='.jpg':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}{convertTo}",format='png')
#             domain=request.get_host()
#             storagePathFromDomain=f"https://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)
#         if convertTo=='.gif' and imageExtension=='.webp':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             image.save(f"{ImageSavingLocation}{randomImageName}{imageExtension}")
#             image=webp.load_images(f"{ImageSavingLocation}{randomImageName}{imageExtension}")
#             im1 = image[0].filter(ImageFilter.DETAIL)
#             im1=im1.filter(ImageFilter.MinFilter(1))
#             im1.save(f"{ImageSavingLocation}{randomImageName}{convertTo}", 'gif', 
#                             save_all=True,lossless=True,append_images=image[0:],
#                             quality=100,allow_mixed=True,minimize_size=False,method=6,
#                             kmax = 1)
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)
#         if convertTo=='.gif' and imageExtension=='.jpg':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}{convertTo}",format='gif')
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)
#         if convertTo=='.webp' and imageExtension=='.jpg':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}{convertTo}",format='webp')
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)
#         if convertTo=='.png' and imageExtension=='.webp':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}{convertTo}",format='png')
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)      
#         if convertTo=='.jpg' and imageExtension=='.webp':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}{convertTo}",format='JPEG')
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)   
#         if  convertTo=='.jpg' and imageExtension=='.tiff':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}{convertTo}",format='JPEG')
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)
#         if  convertTo=='.png' and imageExtension=='.tiff':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}{convertTo}",format='PNG')
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)
#         if  convertTo=='.jpg' and imageExtension=='.png':
#             randomImageName=f"{imageName[:imageName.rindex('.')]}_{randomString}_Converted_From_{imageExtension[1:].upper()}_To_{convertTo[1:].upper()}{convertTo}"
#             RGBImage=image.convert('RGB')
#             RGBImage.save(f"{ImageSavingLocation}{randomImageName}",format='png')
#             # save to database
#             return Response({})
#         if convertTo=='.jpg' and imageExtension=='.bmp':
#             randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#             image.save(f"{ImageSavingLocation}{randomImageName}{convertTo}",format='JPEG')
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data={'convertedFromExtension':imageExtension,
#                 'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertTo}',  
#                   }
#             return self.return_response(data=data)
#         return Response({'detail':'please provide a a valid file path you want to convert to'})
    # def delete(self, request, *args, **kwargs):
    #     if kwargs:
    #         id=kwargs['pk']
    #         if (type(id)==type(1)):
    #             instance=get_object_or_404(ImageConverterModel, pk=id)
    #             if instance:
    #                 ImageSavingLocationFromDomain=instance.convertedImage
    #                 domain=request.get_host()
    #                 storagePathFromDomain=f"http://{domain}/media/"
    #                 ImageName=ImageSavingLocationFromDomain.removeprefix(storagePathFromDomain)
    #                 convertedFromExtension=instance.convertedFromExtension
    #                 convertedToFileExtension=ImageName[ImageName.rindex('.'):]
    #                 fileNameWithoutExtension=ImageName[:ImageName.rindex('.')]
    #                 basePath=Path(__file__).resolve().parent.parent.parent
    #                 path=f"{basePath}\\media\\"
    #                 instance.delete()
    #                 print(convertedFromExtension=='.webp' and convertedToFileExtension==".gif")
    #                 if convertedFromExtension=='.webp' and convertedToFileExtension==".gif":
    #                     os.remove(f'{path}{fileNameWithoutExtension}{convertedFromExtension}')
    #                 try:
    #                     os.remove(f'{path}{ImageName}')
    #                 except FileNotFoundError:
    #                     return Response({'detail':f"{ImageName} is not Available in Your Files"},status=status.HTTP_404_NOT_FOUND)
    #                 return Response({'detail':'Image and Instance Has been Deleted'},status=status.HTTP_204_NO_CONTENT)
    #         return Response({'detail':"instance doesnot exist"})
    #     if not kwargs:
    #         qs=ImageConverterModel.objects.all()
    #         if qs:
    #             for instance in qs :
    #                 ImageSavingLocationFromDomain=instance.convertedImage
    #                 domain=request.get_host()
    #                 storagePathFromDomain=f"http://{domain}/media/"
    #                 ImageName=ImageSavingLocationFromDomain.removeprefix(storagePathFromDomain)
    #                 convertedFromExtension=instance.convertedFromExtension
    #                 convertedToFileExtension=ImageName[ImageName.rindex('.'):]
    #                 fileNameWithoutExtension=ImageName[:ImageName.rindex('.')]
    #                 basePath=Path(__file__).resolve().parent.parent.parent
    #                 path=f"{basePath}\\media\\"
    #                 instance.delete()
    #                 if convertedFromExtension=='.webp' and convertedToFileExtension==".gif":
    #                     os.remove(f'{path}{fileNameWithoutExtension}{convertedFromExtension}')
    #                 try:
    #                     os.remove(f'{path}{ImageName}')
    #                 except FileNotFoundError:
    #                     continue
                        
    #             return Response({'detail':'All instanses deleted'})
    #         else:
    #             return Response({'detail':'all instances are already deleted'})
    #     return Response({"detail":"Something Went Wrong...."})