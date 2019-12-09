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
from wordcloud import WordCloud, STOPWORDS 
# 나중에 안쓰면 스탑워드 남기고 워클만삭제

wiki=wikipediaapi.Wikipedia('ko')
#서머리 빼오는 함수에서 속도를 줄이기 위해서 뺌

komoran = Komoran()
#함수 안에서 계속 생성되는 중복을 방지, 속도 줄이기 위해서 뺌.

def Text_to_list(text_a):
    text = text_a
    text2 = " ".join(text.split())
    #텍스트 전처리(줄바꿈 및 공백이 길어지면 코모란에서 에러가 뜨길래 전처리함)
    text2 = str(text2)
    Text_list = komoran.pos(text2)

    return Text_list


def Counting(list_a, search_word):
    Counting_List = []
    for i in list_a :
        if i[1] == 'NNP' and len(i[0]) > 1:
            Counting_List.append(i[0])
            #i[0]는 1글자가 아닌 고유명사 단어, Counting_List에 모아주는 작업.

    stop_words = [search_word, '(', ')']

    Counting_List = [each_word for each_word in Counting_List if each_word not in stop_words]
    #불용어 제거,

    result = Counter(Counting_List)
    #카운터 객체로 갯수 세줌

    return result
    # collections.Counter 를 반환함, 리스트를 반환하고 싶으면 return Counting_List


def Keywording(Counter_a):
    #지금은 단순 카운팅, 나중에 tf,idf로 적용
    temp_list = []

    list_4 = Counter_a.most_common(4)

    for a in list_4:
        temp_list.append(a[0])
     # 0을 준 이유는 (이름,카운트갯수) 형태에서 이름만 빼오기 위해
    return temp_list

def summary(list_a):
    summary_list = []
    
    for k in list_a :
        page_py = wiki.page(k)
        categories = page_py.categories
        a = categories.get('분류:동음이의어 문서')
        b = categories.get('분류:동명이인 문서')

        if a == None and b == None:
            summary_list.append(page_py.summary[0:100])
        else : 
            summary_list.append("동음 이의어 문서입니다. 해당 키워드를 다시 검색해 주세요.")
            # print(page_py.links.keys())

    return summary_list

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


def result(request):
    if request.method == "POST":
        search_keyword = request.POST.get('search_keyword')
    
    context = {
        'text': search_keyword,
    }
    return render(request, 'Ask_Wiki/result_page.html',context)


def main(request):
    search_keyword = None
    if request.method == "POST":
        search_keyword = request.POST.get('search_keyword')

    if search_keyword == None or search_keyword == "" :
        return render(request, 'Ask_Wiki/error_page.html')
    
    page_py = wiki.page(search_keyword)
    #index 페이지에서 받아온 검색어를 위키페이지 검색으로 바로 넘겨줌

### 예외 처리
    if page_py.exists() == False :
        return render(request, 'Ask_Wiki/error_page.html')
    #index에서 받은 검색어가 존재하지 않는 위키일시 에러페이지로 로딩 

    #동음 이의어 처리
    categories = page_py.categories
    a = categories.get('분류:동음이의어 문서')
    b = categories.get('분류:동명이인 문서')
    if a == None and b == None:
        Links = ""
    else : 
        Links = page_py.links
        context = {
        'links' : Links,
        'search_keyword' : search_keyword,
        }
        return render(request,"Ask_Wiki/same_list.html", context)
### 예외 처리


### 생애, 요약이 있는지 확인하고 가져오는 함수 
    primary_list = []
    primary_list_name=[]
    Counting_List = []
    for section in page_py.sections :
        print(section.title)
        if section.title.find("생애") != -1:
            if len(section.sections) != 0 :
            #서브 섹션이 있는 목록을 거르기 위한 len 확인
                subsection = section.sections
                

                for sub in subsection :
                    print(sub.title)

                    S_pos_list = Text_to_list(sub.text)
                    sub_result = Counting(S_pos_list,search_keyword)

                    for i in S_pos_list :
                        if i[1] == 'NNP' and len(i[0]) > 1:
                            # print(i[0])
                            Counting_List.append(i[0])



                    t = Counter(Counting_List)
                    d =  len(Counting_List)
                    for i in Counting_List :
                        print(f"{i} :  {t[i]/d}")
                        print(f'섹션합 :  {len(subsection)}')

                        print(f'문서 :  {subsection.count(i)}')
                        print(Counting_List.count(i))

                    sub_list = Keywording(sub_result)
                    primary_list.append(sub_list)

                    primary_list_name.append(sub.title)

        elif section.title == "역사":
            print("이거는 역사")

        else :
            print("패스")
            
### 생애, 요약이 있는지 확인하고 가져오는 함수 끝
    



## 단어 카운팅, 깃 합칠때 주석 제거
    # 사용 방법 : Text_to_list() 에 텍스트를 넣음 -> 텍스트 전처리된 리스트화
    # 사용 방법2 : Counting() 에 리스트를 넣음 -> 고유명사로 카운팅
    # 사용 방법3 : 2에서 만든 카운터 객체를 Keywording 함수에 넣고 리스트에 할당
    # ex) 
    # pos_list = Text_to_list(page_py.text)
    # total_result = Counting(pos_list)
    # total_list = Keywording(total_result)


    # 전체 카운팅
    pos_list = Text_to_list(page_py.text)

    # if request.method == "POST":
    #     search_keyword = request.POST.get('search_keyword')
    
    if request.POST.get('original_keyword') == None :
        total_result = Counting(pos_list,search_keyword)
    else : 
        original_keyword = request.POST.get('original_keyword')
        total_result = Counting(pos_list,original_keyword)
    # 동음 이의어 문서에서 링크 타고 들어왔으면 불용어에 original_keyword를 사용

    total_list = Keywording(total_result)

    #전체 키워드의 요약 내용
    total_summary = summary(total_list)

## 전체 카운팅 끝
    
    primary_list.reverse()
    context = {
        'total_keyword' : total_list,
        'total_summary' : total_summary,
        'primary_keyword' : primary_list,
        'primary_keyword_name' : primary_list_name,
        'title' : page_py.title,
        'test': page_py.title,
        'links' : Links,
    }

    # return render(request,"Ask_Wiki/main.html", context)
    return render(request,"Ask_Wiki/mindmap.html", context)


def link(request, link):
    wiki=wikipediaapi.Wikipedia('ko')
    page_py = wiki.page(link) 

    context = {
        'total' : page_py.text,
        'title' : page_py.title,
        'summary': page_py.summary[0:500],
        'links' : page_py.links,

    }
    return redirect('Ask:detail')

