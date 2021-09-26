from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('main', views.main, name='main'),
    path('<str:room_name>/', views.room, name='room'),
]
