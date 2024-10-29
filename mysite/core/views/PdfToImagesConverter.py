from .imports import *
import fitz
from ..models import PdfToImagesModel
from ..serializers import PdfToImagesSerializer
from django.core.files.base import ContentFile
from django.conf import settings
class PdfToImagesView(generics.ListCreateAPIView):
    queryset = PdfToImagesModel.objects.all()
    serializer_class = PdfToImagesSerializer

    def post(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                pdf_file = instance.document
                if not pdf_file.name.endswith('.pdf'):
                    return Response({"error": "File must be a PDF."}, status=400)
                
                # Open the PDF document
                pdf_path = pdf_file.path
                doc = fitz.open(pdf_path)
                image_urls = []

                # Convert each page to an image
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    
                    # Save each page image
                    img_name = f"{os.path.splitext(pdf_file.name)[0]}_page_{page_num + 1}.png"
                    img_content = ContentFile(pix.tobytes("png"))
                    # Save the image to converted_images\pdf_name_folder\ directory
                    converted_image_path = f"converted_images/{os.path.basename(pdf_file.name[:-4])}_images/{os.path.basename(img_name)}"
                    instance.document.storage.save(converted_image_path, img_content)
                    
                    # Collect the URL
                    image_url = request.build_absolute_uri(instance.document.storage.url(converted_image_path))
                    image_urls.append(image_url)
                
                # Update instance with converted images URLs
                instance.converted_images = image_urls
                instance.save()

                return Response({
                    "document": request.build_absolute_uri(instance.document.url),
                    "converted_images": image_urls
                })

            return Response(serializer.errors, status=400)

    def delete(self, request, *args, **kwargs):
        instances = self.get_queryset()
        deleted_files = []
        
        # Iterate through all instances and delete their files
        for instance in instances:
            if instance.document:
                pdf_name=os.path.basename(instance.document.name)
                deleted_files.append(instance.document.path)  # Keep track of deleted files
                instance.document.delete(save=False)  # Delete the file from storage
            
            # Also delete any converted images if they exist
            if instance.converted_images:
                for img_path in instance.converted_images:
                    # Extract the file name from the URL
                    img_file_name = os.path.basename(img_path)
                    img_full_path = instance.document.storage.path(f"converted_images/{pdf_name[:-4]}_images")
                    try:
                        if os.path.isfile(img_full_path):
                            os.remove(img_full_path) 
                        else:
                            print(f"Image not found:  {img_full_path}")  
                    except Exception as e:
                        print(f"Error deleting image {img_full_path}: {e}")  # Log any error during deletion
            
            instance.delete()  # Delete the instance from the database

        return Response({"message": "All records and files deleted successfully.", "deleted_files": deleted_files}, status=204)
    

# class PdfToImage(generics.ListCreateAPIView,generics.DestroyAPIView,generics.RetrieveAPIView):
#     queryset=PdfToImageModel.objects.all()
#     serializer_class=PdfToImageSerializer
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
#     def get(self,request,*args,**kwargs):
#         pk=kwargs.get('pk')
#         if pk is not None:
#             return self.retrieve(request,*args,**kwargs)
#         return self.list(request,*args,**kwargs)
#     def post(self,request,*args,**krargs):
#         imageName=request.data['image'].name
#         inComingImageFile=request.data['image']
#         InComingFileExtension=imageName[imageName.rindex('.'):]
#         convertToFileExtension=request.data['convert_to']
#         randomString=f"{datetime.datetime.now().date()}_{str(datetime.datetime.now().time()).replace('.','').replace(':','')}"
#         basePath=Path(__file__).resolve().parent.parent.parent
#         imagePath=f"{basePath}\media\\"
#         if convertToFileExtension=='.jpg' and InComingFileExtension=='.pdf':
#             randomDirectoryName=f"{self.generate_random_string()}_{randomString}"
#             os.mkdir(f'{imagePath}{randomDirectoryName}')
#             pdfName=default_storage.save(f"{randomDirectoryName}\{imageName}",inComingImageFile)
#             print(randomDirectoryName)
#             images = convert_from_path(f"{imagePath}{pdfName}")
#             domain=request.get_host()
#             storagePathFromDomain=f"http://{domain}/media/"
#             data= {
#             "folderName": randomDirectoryName,
#             "Image": ""
#             }
#             if len(images)<=5:
#                 for i in range(len(images)):
#                     # for multiple images
#                         randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#                         images[i].save(f'{imagePath}{randomDirectoryName}\{randomImageName}.jpg', 'JPEG')
#                         data["Image"]=f"{storagePathFromDomain}{randomDirectoryName}/{randomImageName}.jpg"
#                         serializer = self.get_serializer(data=data)
#                         serializer.is_valid(raise_exception=True)
#                         serializer.save()
#             else:
#                 for i in range(5):
#                     # for multiple images
#                         randomImageName=f"image_{randomString}_{self.generate_random_string()}"
#                         images[i].save(f'{imagePath}{randomDirectoryName}\{randomImageName}.jpg', 'JPEG')
#                         data["Image"]=f"{storagePathFromDomain}{randomDirectoryName}/{randomImageName}.jpg"
#                         serializer = self.get_serializer(data=data)
#                         serializer.is_valid(raise_exception=True)
#                         serializer.save()
#                 qs=PdfToImageModel.objects.filter(folderName=randomDirectoryName)
#                 serializer = PdfToOnlyImageSerializer(qs,many=True)
#                 headers = self.get_success_headers(serializer.data)
#                 serializer.data.append({'message':"You cannot convert more than 5 pages"})
#                 return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#             qs=PdfToImageModel.objects.filter(folderName=randomDirectoryName)
#             serializer = PdfToOnlyImageSerializer(qs,many=True)
#             headers = self.get_success_headers(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#         return Response({'detail':'something went Wrong'})
#     def delete(self,request,*args,**kwargs):
#             if kwargs:
#                 id=kwargs['pk']
#                 if (type(id)==type(1)):
#                     instance=get_object_or_404(PdfToImageModel, pk=id)
#                     if instance:
#                         FolderName=instance.folderName
#                         basePath=Path(__file__).resolve().parent.parent.parent
#                         path=f"{basePath}\media\\"
#                         instance.delete()
#                         try:
#                             shutil.rmtree(path+FolderName)
#                         except FileNotFoundError:
#                             return Response({'detail':f"{FolderName} is not Available in Your Files"},status=status.HTTP_404_NOT_FOUND)
#                         return Response({'detail':'Image and Instance Has been Deleted'},status=status.HTTP_204_NO_CONTENT)
#                 return Response({'detail':"instance doesnot exist"})
#             if not kwargs:
#                 qs=PdfToImageModel.objects.all()
#                 if qs:
#                     for instance in qs :
#                         FolderName=instance.folderName
#                         basePath=Path(__file__).resolve().parent.parent.parent
#                         path=f"{basePath}\media\\"
#                         instance.delete()
#                         try:
#                             shutil.rmtree(path+FolderName)
#                         except FileNotFoundError:
#                             continue
                            
#                     return Response({'detail':'All instanses deleted'})
#                 else:
#                     return Response({'detail':'all instances are already deleted'})
#             return Response({"detail":"Something Went Wrong...."})