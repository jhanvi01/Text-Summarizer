import imp
from pydoc import doc
from unittest.mock import sentinel
from django.shortcuts import render
from prometheus_client import Summary
from soupsieve import select
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest


def home(request):
    output=""
    if request.method=="POST":
        intext=request.POST['intext']
        # intext=''''''

        stopwords= list(STOP_WORDS)
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(intext)
        tokens = [token.text for token in doc ]
        # print(tokens)
        punctuations = punctuation +'\n'
        # print(punctuations)

        word_frequencies={}
        for word in doc:
            if word.text.lower() not in stopwords:
                if word.text.lower() not in punctuations:
                    if word.text not in word_frequencies.keys():
                        word_frequencies[word.text]=1
                    else:
                        word_frequencies[word.text]+=1

        # print(word_frequencies)
        max_frequency = max(word_frequencies.values())
        # print(max_frequency)

        for word in word_frequencies.keys():
            word_frequencies[word]=word_frequencies[word]/max_frequency
        # print(word_frequencies)    

        sentence_tokens= [sent for sent in doc.sents]
        # print(sentence_tokens)

        sentence_scores ={}
        for sent in sentence_tokens:
            for word in sent:
                if word.text.lower() in word_frequencies.keys():
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent]= word_frequencies[word.text.lower()]
                    else:
                        sentence_scores[sent]+= word_frequencies[word.text.lower()]

        # print(sentence_scores)

        select_length = int(len(sentence_scores)*0.3)
        # print(select_length)

        summary= nlargest(select_length, sentence_scores, key=sentence_scores.get)
        # print(summary)

        final_summary = [word.text for word in summary]
        # print(final_summary)

        summary = ' '.join (final_summary)
        print(summary)
        return render(request,'index.html',{'output':summary})

    return render(request,"index.html")
