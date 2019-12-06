from django.urls import path
from . import views

app_name = "Ask"

urlpatterns =[
    path('', views.index, name="index"),
    path('search_wiki/', views.ajax, name="ajax"),
    path('main/', views.main, name="main"),

    path('result/',views.result, name="result"), # 결과화면

]