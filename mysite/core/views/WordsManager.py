from .imports import *
class WordManager(APIView):
    def post(self,request,*args,**kwargs):
        if request.data['purpose']=='wordcount':
            words=request.data['words']
            print(request.data)
            words_count=len(words.split())
            return Response({'wordCount':words_count})
        if request.data['purpose']=='lowertouppercase':
            words=request.data['words']
            upperCaseWords=words.upper()
            return Response({'UpperCase':upperCaseWords})
        if request.data['purpose']=='spellingcheck':
            spell = SpellChecker()
            words=request.data['words'].split()
            wordlist=['let', 'us', 'wlak','on','the','groun']
            misspelled=spell.unknown(wordlist)    
            misspelledWithIndex,corrected,candidates,correctedString=[]
            for word in misspelled:
                misspelledWithIndex.append(wordlist.index(word))
                misspelledWithIndex.append(word)
                corrected.append(wordlist.index(word))     
                corrected.append(spell.correction(word))
                candidates.append(wordlist.index(word)) 
                candidates.append(word)
                candidates.append(spell.candidates(word))
                index=-1
            for word in wordlist:
                index=index+1
                for misspell in misspelled:
                    index=index+1
                    if word==misspell:
                        correctedString.append(corrected[index])
                    else:
                        correctedString.append(word)
                        
            return Response({'Missplled':misspelledWithIndex,'Most Likely Words':corrected,'Candidates Words':candidates,'corrected string':correctedString})