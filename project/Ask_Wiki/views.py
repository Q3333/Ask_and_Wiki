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
    

### 생애, 요약이 있는지 확인하고 가져오는 함수
    page_py.sections[0].title,

    for section in page_py.sections :
        print(section.title)
        if section.title == "생애" :
            print("여기부터 생애처리")
            break
        elif section.title == "역사":
            print("이거는 역사")
        else :
            print("이거는 요약에서 처리하셈")
            
        #12-05 조규상 할일 : 생에에서 서브섹션 있는지 체크하는지 해야함
### 생애, 요약이 있는지 확인하고 가져오는 함수 끝
    


#### 여기부터 형태소분석

    # text = page_py.text
    text = page_py.text
    text2 = " ".join(text.split())
    text2 = str(text2)
    #텍스트 전처리(줄바꿈 및 공백이 길어지면 코모란에서 에러가 뜨길래 전처리함)

    komoran = Komoran()

    pos_list = komoran.pos(text2)
    print(type(pos_list))


    NNP_List = []
    for i in pos_list :
        if i[1] == 'NNP' :
            # print(i[0])
            NNP_List.append(i[0])


    result = Counter(NNP_List)
    print(result)


    #단어를 리스트에 추가해서 카운트 갯수 세는 부분
    
    # print(pos_list[1][1])
    # print(pos_list[2][1])

#### 형태소 분석 끝


    # print(page_py.sections[0].sections[0])
    print(page_py.sections[0])

    context = {
        'total' : page_py.text,
        'title' : page_py.title,
        'subsection' : page_py.sections[2].sections[2], #subsection 내용
        'subsection_title' : page_py.sections[2].sections[2].title, #subsection 타이틀
        'summary': page_py.summary[0:500],
        'test': page_py.sections[0].title,
        'link' : page_py.links.get,

    }
    return render(request,"Ask_Wiki/index.html", context)
