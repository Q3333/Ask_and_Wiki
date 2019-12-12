from django.urls import path, re_path
from . import views

app_name = "Ask"

urlpatterns =[
    path('', views.index, name="index"),
    path('main/', views.main, name="main"),
    # path('link/<str:link>/', views.link, name="link"),
    re_path(r'^link/(?P<link>[^`]+)/$', views.link, name="link"),
    path('result/',views.result, name="result"), # 결과화면

]
