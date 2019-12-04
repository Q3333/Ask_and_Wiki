from django.shortcuts import render,redirect
import wikipediaapi
import konlpy
import nltk
from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Okt
from konlpy.tag import Komoran
from collections import Counter



def index(request):
    wiki=wikipediaapi.Wikipedia('ko')
    page_py = wiki.page('조조') 
    # print("Page - Exists: %s" % page_py.exists())
    # print("Page - Title: %s" % page_py.title)
    # print("Page - Summary: %s" % page_py.summary[0:100])

    # sec1 = page_py.sections[0:1][0]
  
    
#### 여기부터 형태소분석

    # text = page_py.text
    text = page_py.summary[0:500]
    
    text2 = str(text)
 

    komoran = Komoran()

    pos_list = komoran.pos(text2)
    print(type(pos_list))

    for i in pos_list :
        if i[1] == 'NNP' :
            print(i[0])
    
    # print(pos_list[1][1])
    # print(pos_list[2][1])

    context = {
        'total' : page_py.text,
        'title' : page_py.title,
        'subsection' : page_py.sections[2].sections[2], #subsection 내용
        'subsection_title' : page_py.sections[2].sections[2].title, #subsection 타이틀
        'summary': page_py.summary[0:500],
        'link' : page_py.links.get,

    }
    return render(request,"Ask_Wiki/index.html", context)
