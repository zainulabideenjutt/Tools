from .imports import *
class AudioDownloader(APIView):
    def post(self,request,*args,**kwargs):
        yt = YouTube('https://www.youtube.com/watch?v=oTKtF3IzamM')
        audio=yt.streams.filter(only_audio=True).desc().first().url   
        data={'Audio':audio}
        return Response(data)