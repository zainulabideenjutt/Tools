from .imports import *
class ImagesToPdf(generics.ListCreateAPIView,generics.RetrieveAPIView):
    queryset=ImagestoPdfModel.objects.all()
    serializer_class=ImagesToPdfSerializer
    def return_response(self,**data):
            serializer = self.get_serializer(data=data['data'])
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def get(self,request,*args,**kwargs):
        pk=kwargs.get('pk')
        if pk is not None:
            return self.retrieve(request,*args,**kwargs)
        return self.list(request,*args,**kwargs)
    def post(self,request,*args,**kwargs):
        images=[]
        images.append(request.data.get('image1') or "")
        images.append(request.data.get('image2') or "")
        images.append(request.data.get('image3') or "")
        images.append(request.data.get('image4') or "")
        images.append(request.data.get('image5') or "")
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
                    instance=get_object_or_404(ImagestoPdfModel, pk=id)
                    if instance:
                        pdfName=instance.pdfName
                        basePath=Path(__file__).resolve().parent.parent.parent
                        path=f"{basePath}\media\\"
                        instance.delete()
                        try:
                            os.remove(f'{path}{pdfName}')
                        except FileNotFoundError:
                            return Response({'detail':f"{pdfName} is not Available in Your Files"},status=status.HTTP_404_NOT_FOUND)
                        return Response({'detail':'Image and Instance Has been Deleted'},status=status.HTTP_204_NO_CONTENT)
                return Response({'detail':"instance doesnot exist"})
            if not kwargs:
                qs=ImagestoPdfModel.objects.all()
                if qs:
                    for instance in qs :
                        pdfName=instance.pdfName
                        basePath=Path(__file__).resolve().parent.parent.parent
                        path=f"{basePath}\media\\"
                        instance.delete()
                        try:
                            os.remove(f'{path}{pdfName}')
                        except FileNotFoundError:
                            continue
                            
                    return Response({'detail':'All instanses deleted'})
                else:
                    return Response({'detail':'all instances are already deleted'})
            return Response({"detail":"Something Went Wrong...."})