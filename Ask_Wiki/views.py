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
from wordcloud import STOPWORDS
import math
import operator 
# 나중에 안쓰면 스탑워드 남기고 워클만삭제
from .models import Wiki 

wiki=wikipediaapi.Wikipedia('ko')
#서머리 빼오는 함수에서 속도를 줄이기 위해서 뺌

komoran = Komoran()
#함수 안에서 계속 생성되는 중복을 방지, 속도 줄이기 위해서 뺌.

final_list = []

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


def Keywording(Counter_a, number):
    #서브섹션이 존재하는 경우 tf,idf로 적용
    
    number = int(number)
    temp_list = []

    list_4 = Counter_a.most_common(number)

    for a in list_4:
        temp_list.append(a[0])
     # 0을 준 이유는 (이름,카운트갯수) 형태에서 이름만 빼오기 위해
    return temp_list

def summary(list_a):
    
    for k in list_a :
        final_temp_list = []
        DB = Wiki.objects.all()
        check_DB = DB.filter(title=k)
        check_DB2 = []
        
        if len(check_DB) == 0 :
            print(f"DB 새로 추가, 단어 이름 : {k}")
            page_py = wiki.page(k)
            categories = page_py.categories
            c = categories.get('분류:동음이의어 문서')
            b = categories.get('분류:동명이인 문서')

            DB_wiki = Wiki()
            DB_wiki.title = page_py.title

            final_temp_list.append(page_py.title)

            if c == None and b == None:
                a = page_py.summary
                check_DB2 = DB.filter(summary=a[:a.find('\n')])
                DB_wiki.summary = a[:a.find('\n')]
                final_temp_list.append(a[:a.find('\n')])

            else : 
                DB_wiki.summary = "동음 이의어 문서입니다. 해당 키워드를 다시 검색해 주세요."
                final_temp_list.append("동음 이의어 문서입니다. 해당 키워드를 다시 검색해 주세요.")
            
            if len(check_DB2) == 0 :
                DB_wiki.save()
            

            final_list.append(final_temp_list)

        else : 
            print(f"이건 이미 DB에 있는 값임, 단어 이름 : {k} ")
            final_temp_list.append(check_DB[0].title)
            final_temp_list.append(check_DB[0].summary)
            final_list.append(final_temp_list)

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

def tf_idf(t,d,D):
    tf = float(d.count(t)) / sum(d.count(w) for w in set(d))
    idf = math.log( float(len(D))/ (len([doc for doc in D if t in doc])) )
    return tf*idf

def main(request):
    DB = Wiki.objects.all()
    search_keyword = None
    
    if request.method == "POST":
        search_keyword = request.POST.get('search_keyword')
        number = request.POST.get('num')
        # number는 가지 개수, 초기 화면에선 4개로 고정
        if number == None :
            number = str(4)

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


### 서브섹션 존재하는지 체크하고 처리하는 함수(기존 생애, 역사 등)
    second_keyword_name = []
    # primary_list -> second_keyword_name 로 변경
    first_keyword_name=[]
    # primary_list_name -> first_keyword_name 로 변경
    Counting_List = []
    tfidf_list = []
    sub_final_list = []

    for section in page_py.sections :
        if section.title.find("생애") != -1:
            tf_len = len(section.sections)
            if len(section.sections) != 0 :
            #서브 섹션이 있는 목록을 거르기 위한 len 확인
                subsection = section.sections
                

                for sub in subsection :
                    a = sub.text
                    sub_key_title = f"{search_keyword}_{sub.title}"

                    final_temp2_list = []
                    check_DB = DB.filter(title=sub_key_title)
                    if len(check_DB) == 0 :
                        DB_wiki = Wiki()
                        DB_wiki.title = sub_key_title
                        DB_wiki.summary = a[:a.find('\n')]
                        
                        DB_wiki.save()
                        
                        final_temp2_list.append(sub_key_title)
                        final_temp2_list.append(a[:a.find('\n')])
                        final_list.append(final_temp2_list)
                        
                    else :
                        final_temp2_list.append(check_DB[0].title)
                        final_temp2_list.append(check_DB[0].summary)
                        final_list.append(final_temp2_list)

                    S_pos_list = Text_to_list(sub.text)

                    
                    first_keyword_name.append(sub_key_title)
                    #위치 바꿈


                    

                    section_list = []
                    for i in S_pos_list :
                        if i[1] == 'NNP' and len(i[0]) > 1:
                            section_list.append(i[0])
                    Counting_List.append(section_list)
                    
                    


                D = sum(Counting_List, [])
                for d in Counting_List :
                    print(Counting_List)
                    tfidf = {}
                    for t in d:
                        # print(f'{t} : {tf_idf(t,d,D)}')
                        if t == search_keyword :
                            continue
                        tfidf[t] = tf_idf(t,d,D)
                    tfidf_list.append(tfidf)
                count = 0
                while(count < tf_len) :
                    tfidf_list_sorted = sorted(tfidf_list[count].items(), key = operator.itemgetter(1), reverse=True)
                    count += 1
                    # print(tfidf_list_sorted[:int(number)])
                    sub_temp_list = []
                    for name in tfidf_list_sorted[:int(number)] :
                        # print(f"섹션 {count} 번쨰")

                        sub_temp_list.append(name[0])
                    sub_final_list.append(sub_temp_list)    
    
                # second_keyword_name = sub_final_list  
                second_keyword_name = sum(sub_final_list, [])       
                summary(second_keyword_name) 
                second_keyword_name = sub_final_list  
              
                        

                # // 1. primary list 에서 키워드 중복 제거 chain  keywords = 중복제거한 prilist
                # 2. 중복된 키워드를 가지고 primary list 2중 배열 -> for 문으로 돌리는데 중복이 있을수 있으니 set()
                # for i in Counting_List :
                #     print(f"{i} 전체문서 : {sum(second_keyword_name, []).count(i)}")

        else :
            print("패스")
   
            
### 서브섹션 존재하는지 체크하고 처리하는 함수 끝
    
    


### 텍스트 전처리, 카운팅
    # 사용 방법 : Text_to_list() 에 텍스트를 넣음 -> 텍스트 전처리된 리스트화
    # 사용 방법2 : Counting() 에 리스트를 넣음 -> 고유명사로 카운팅
    # 사용 방법3 : 2에서 만든 카운터 객체를 Keywording 함수에 넣고 리스트에 할당
    # ex) 
    # pos_list = Text_to_list(page_py.text)
    # total_result = Counting(pos_list)
    # total_list = Keywording(total_result)


    # 전체 카운팅
    pos_list = Text_to_list(page_py.text)
    # 동음 이의어 문서에서 링크 타고 들어왔으면 불용어에 original_keyword를 사용
    if request.POST.get('original_keyword') == None :
        total_result = Counting(pos_list,search_keyword) 
    else : 
        original_keyword = request.POST.get('original_keyword')
        total_result = Counting(pos_list,original_keyword)
        page_py = wiki.page(original_keyword)
        

    
### 키워드의 타이틀, 서머리 DB에 넣는 곳

    

    final_temp3_list = []
    keyword = Wiki()
    keyword.title = page_py.title
    a = page_py.summary
    keyword.summary = a[:a.find('\n')]

    keyword.save()

    final_temp3_list.append(page_py.title)
    final_temp3_list.append(a[:a.find('\n')])
    final_list.append(final_temp3_list)

### 키워드 타이틀, 서머리 작업 끝

    

    # 서브섹션 없는 키워드 다루는 부분
    if len(first_keyword_name) == 0:
        first_keyword_name = Keywording(total_result,number)
        summary(first_keyword_name)


        # 두번째 서머리 다루는 부분
        for single_keyword in first_keyword_name :

            page_py2 = wiki.page(single_keyword)

            categories = page_py2.categories
            a = categories.get('분류:동음이의어 문서')
            b = categories.get('분류:동명이인 문서')

            if a == None and b == None:
                pos_list = Text_to_list(page_py2.text)
                total_result = Counting(pos_list,single_keyword)
                
                second_keyword_list= Keywording(total_result,number)
                summary(second_keyword_list)
                second_keyword_name.append(second_keyword_list)

            else : 
                print("동음 이의어 문서입니다.")


### 텍스트 전처리, 카운팅 끝

    # DB 데이터 업데이트 안되었으면 아래에서 한번 더 선언해줌
    second_keyword_name.reverse()
    second_keyword_name3 = [["aa","11"],["bb","22"]]
    DB = Wiki.objects.all()
#서머리 가져오는게 렉걸려서 DB에 넣어서 확인, DB에 없으면 서머리함수, 있으면 패스

    context = {
        'DB2' : DB,
        'second_summary' : "",
        'total_summary' : "",
        'second_keyword_name' : second_keyword_name,
        'second_keyword_name3' : final_list,
        'first_keyword_name' : first_keyword_name,
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

