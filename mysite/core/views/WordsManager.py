from .imports import *
class WordManager(APIView):
    def post(self,request,*args,**kwargs):
        purpose=request.query_params.get('purpose')
        if purpose=='wordcount':
            words=request.query_params.get('words')
            words_count=len(words.split())
            return Response({'wordCount':words_count})
        if purpose=='lowertouppercase':
            words=request.query_params.get('words')
            upperCaseWords=words.upper()
            return Response({'UpperCase':upperCaseWords})
        if purpose=='spellingcheck':
            spell = SpellChecker()
            words=request.query_params.get('words').split()
            wordlist=words
            misspelled=spell.unknown(wordlist)    
            misspelledWithIndex=[]
            corrected=[]
            candidates=[]
            correctedString=[]
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
            if correctedString :
                correctedString=correctedString.join()
            return Response({'Missplled':misspelledWithIndex,'Most Likely Words':corrected,'Candidates Words':candidates,'corrected string':correctedString})