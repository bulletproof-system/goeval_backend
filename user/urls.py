from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='Login'),
    path('getInfo/',views.get_info,name = 'getInfo')
]