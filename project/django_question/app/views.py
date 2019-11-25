from django.shortcuts import render, redirect
from .models import Question,Choice
import wikipediaapi

# Create your views here.
def index(request):

    wiki=wikipediaapi.Wikipedia('ko')
    page_py = wiki.page('조조') 
    # print("Page - Exists: %s" % page_py.exists())
    # print("Page - Title: %s" % page_py.title)
    # print("Page - Summary: %s" % page_py.summary[0:100])

    print(type(page_py.sections))

    # wiki = wikipediaapi.Wikipedia(
    #     language='ko',
    #     extract_format=wikipediaapi.ExtractFormat.WIKI)

    # p_wiki = wiki.page("조조")
    # print(p_wiki.text)
    # with open("조조.txt", "w") as f: f.write(p_wiki.text)

    sec1 = page_py.sections[0:1][0]
    print(type(sec1))
    print(sec1)

    # sec1_string = " ".join(sec1)
    # print(type(sec1_string))
    # # sec1_split = sec1.split("Subsections ")
    # # print(sec1)

    questions = Question.objects.all()
    context = {
        'questions': questions,
        'total' : page_py.text,
        'title' : page_py.title,
        'sections_1' : page_py.sections[0:1],
        'sections_2' : page_py.sections[1:2],
        'summary': page_py.summary[0:500],

    }
    return render(request,"app/index.html",context)

def detail(request,q_id):
    q = Question.objects.get(id=q_id)

    choices = q.choice_set.all()

    context ={
        'q' : q ,
        'choices' : choices
    }

    return render(request,"app/detail.html",context)

def new(request):
    if request.method == "POST":
        q = Question(question=request.POST.get('title'))
        q.save()
        return redirect('app:index')
    else:
    # 폼 html 을 불러오는 부분.
        return render(request,"app/new.html")
    

def delete(request, q_id):
    q = Question.objects.get(id=q_id)
    q.delete()
    return redirect('app:index')


def choice_edit(request,q_id,c_id):
    q = Question.objects.get(id=q_id)
    cho = Choice.objects.get(id=c_id)

    if request.method == "POST":

        c_text = request.POST.get('c_text')

        cho.survey = c_text
        cho.save()
        return redirect("app:detail", q_id)

    else :
        context = {
            'choice' : cho,
            'q': q
        }
        return render(request,"app/choice_edit.html", context)
     

def choice_del(request, q_id, c_id):
    c = Choice.objects.get(id=c_id)
    c.delete()
    return redirect('app:detail', q_id)

def survey(request,q_id):
    q_text = request.POST.get('q_text')
    q = Question.objects.get(id=q_id)
    c = Choice()
    c.survey = q_text
    c.question = q
    c.save()
    return redirect('app:detail', q_id)
    
def choice_vote(request,q_id,c_id):
    c = Choice.objects.get(id=c_id)
    
    print(f'vote method is {request.method}')
    c.votes = c.votes+1
    c.save()
    return redirect('app:detail', q_id)