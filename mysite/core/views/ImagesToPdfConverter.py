from .imports import *
class ImagesToPdf(APIView):
    def return_response(self,**data):
            serializer = self.get_serializer(data=data['data'])
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def post(self,request,*args,**kwargs):
        images=[]
        if request.data['image1'] != '':
            images.append(request.data['image1'])
            if request.data['image2'] != '':
                images.append(request.data['image2'])
                if request.data['image3'] != '':
                    images.append(request.data['image3'])
                    if request.data['image4'] != '':
                        images.append(request.data['image4'])
                        if request.data['image5'] != '':
                            images.append(request.data['image5'])
        allimages = [
        Image.open(f).convert('RGB')
        for f in images
        ]
        randomString=f"{datetime.datetime.now().date()}_{str(datetime.datetime.now().time()).replace('.','').replace(':','')}"
        basePath=Path(__file__).resolve().parent.parent.parent
        mediaPath=f"{basePath}\media\\"
        pdf_path = mediaPath+randomString+'.pdf'
        pdfName=randomString+'.pdf'
        data={'pdfName':pdfName}
        allimages[0].save(pdf_path, "PDF" ,resolution=100, save_all=True, append_images=allimages[1:])
        return self.return_response(data=data)
    def delete(self,request,*args,**kwargs):
            if kwargs:
                id=kwargs['pk']
                if (type(id)==type(1)):
                    instance=get_object_or_404(PdfToImageModel, pk=id)
                    if instance:
                        FolderName=instance.folderName
                        basePath=Path(__file__).resolve().parent.parent.parent
                        path=f"{basePath}\media\\"
                        instance.delete()
                        try:
                            shutil.rmtree(path+FolderName)
                        except FileNotFoundError:
                            return Response({'detail':f"{FolderName} is not Available in Your Files"},status=status.HTTP_404_NOT_FOUND)
                        return Response({'detail':'Image and Instance Has been Deleted'},status=status.HTTP_204_NO_CONTENT)
                return Response({'detail':"instance doesnot exist"})
            if not kwargs:
                qs=PdfToImageModel.objects.all()
                if qs:
                    for instance in qs :
                        FolderName=instance.folderName
                        basePath=Path(__file__).resolve().parent.parent.parent
                        path=f"{basePath}\media\\"
                        instance.delete()
                        try:
                            shutil.rmtree(path+FolderName)
                        except FileNotFoundError:
                            continue
                            
                    return Response({'detail':'All instanses deleted'})
                else:
                    return Response({'detail':'all instances are already deleted'})
            return Response({"detail":"Something Went Wrong...."})