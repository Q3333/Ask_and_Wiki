from django.shortcuts import render,redirect
from django.http import HttpResponse
import wikipediaapi
import konlpy
import nltk
from konlpy.tag import Hannanum
from konlpy.tag import Kkma
from konlpy.tag import Okt
from konlpy.tag import Komoran
from collections import Counter
import simplejson 


def Text_to_list(text_a):
    komoran = Komoran()
    text = text_a
    text2 = " ".join(text.split())
    #텍스트 전처리(줄바꿈 및 공백이 길어지면 코모란에서 에러가 뜨길래 전처리함)
    text2 = str(text2)
    Text_list = komoran.pos(text2)

    return Text_list


def Counting(list_a):
    Counting_List = []
    for i in list_a :
        if i[1] == 'NNP' :
            # print(i[0])
            Counting_List.append(i[0])

    result = Counter(Counting_List)
    return result
    # collections.Counter 를 반환함, 리스트를 반환하고 싶으면 return Counting_List


    
def index(request):

    return render(request, 'Ask_Wiki/index.html')

def ajax(request):
    # request.POST.get('json형식 안의 내용') from html
    from_html_text = request.POST.get('text')
    print(from_html_text)

    context = {
        'text_return': 'aaaaa',
        'text_return2': '서버에서 보낸data',
    }
    
    return HttpResponse(simplejson.dumps(context), 'Ask_Wiki/index.html')

def main(request):
    wiki=wikipediaapi.Wikipedia('ko')
    page_py = wiki.page('조조') 
    #페이지 존재하는지 확인하는 명령어
    #print("Page - Exists: %s" % page_py.exists())


### 생애, 요약이 있는지 확인하고 가져오는 함수 
    subsection = []

    for section in page_py.sections :
        print(section.title)
        if section.title == "생애" :
            print("여기부터 생애처리")
            print(len(section.sections))
            if len(section.sections) != 0 :
                subsection = section.sections

            break

        elif section.title == "역사":
            print("이거는 역사")

        else :
            print("이거는 요약에서 처리하셈")
            
        
### 생애, 요약이 있는지 확인하고 가져오는 함수 끝
    


#### 여기부터 형태소분석

    


## 단어 카운팅, 깃 합칠때 주석 제거
    # 사용 방법 : Text_to_list() 에 텍스트를 넣음 -> 텍스트 전처리된 리스트화
    # 사용 방법2 : Counting() 에 리스트를 넣음 -> 고유명사로 카운팅
    # ex) 
    # pos_list = Text_to_list(page_py.text)
    # total_result = Counting(pos_list)
    # print(total_result)


    # 전체 카운팅
    pos_list = Text_to_list(page_py.text)
    total_result = Counting(pos_list)
    # print(total_result)

    # 서브1 카운팅
    pos_list_sub0 = Text_to_list(subsection[0].text)
    sub_result = Counting(pos_list_sub0)

    # print(sub_result.title)
    print(dir(sub_result))
    print(sub_result.popitem)

    # 할일 : 
    # dir로 카운터에서 단어 뽑기, 서브섹션 있으면 1~5 카운팅 하기, 전체 카운팅하기, 
    # 해서 콘텍스트로 html 보내기까지 12-05할일

## 단어 카운팅 끝

    links = page_py.links
    for title in sorted(links.keys()):
        print("%s" % (links[title])) 

    #단어를 리스트에 추가해서 카운트 갯수 세는 부분
    
    # print(pos_list[1][1])
    # print(pos_list[2][1])

#### 형태소 분석 끝


    # print(type(page_py.sections[0]))
    # print(type(page_py.sections[0].sections))
    # print(dir(page_py.sections[0]))
    # print(page_py.sections[0].sections)
    # print(len(page_py.sections[0].sections))

    # print(subsection[0].title)
    # print(type(subsection))
    

    context = {
        'total' : page_py.text,
        'title' : page_py.title,
        'subsection' : page_py.sections[2].sections[2], #subsection 내용
        'subsection_title' : page_py.sections[2].sections[2].title, #subsection 타이틀
        'summary': page_py.summary[0:500],
        'test': page_py.sections[0].title,
        'links' : page_py.links,

    }
    return render(request,"Ask_Wiki/main.html", context)
