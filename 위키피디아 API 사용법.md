# 위키피디아 API 사용법

#### 설치 : 

```
pip install wikipedia-api
```



#### 사용 :

```python
wiki=wikipediaapi.Wikipedia('ko')	#언어설정
    page_py = wiki.page('조조') #여기서 키워드 변경
    print("Page - Exists: %s" % page_py.exists()) # 페이지가 존재하는지 체크
    total = page_py.text # 토탈 가져오기
    title = page_py.title # 타이틀 가져오기
    sec1 = page_py.sections[0:1] # 섹션 받아오기
    summary = page_py.summary[0:500] # 요약 가져오기
```



#### 사용할 때 type으로 형태 체크 하고 쓰는 것이 중요