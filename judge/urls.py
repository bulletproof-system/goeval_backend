from django.urls import path

from . import views

urlpatterns = [
    path('login', views.Login, name='Login'),
    path('register',views.Register, name = 'Register'),
    path('getInfo',views.get_info, name = 'getInfo'),
    path('recommend', views.recCourse, name = 'recommend'),
    path('search', views.seaCourse, name = 'search'),
    path('autocomplete', views.autocomplete, name = 'autocomplete'),
    path('detail', views.detail, name = 'detail'),
    path('announcement', views.acqAnnouncement, name = 'announcement'),
    # path('notification', views.acqNotification(), name = 'notification'),
    path('read', views.signRead, name = 'read'),
    path('operate/email', views.changeEmail, name = 'operate/email'),
    path('operate/password', views.changePassword, name = 'operate/password')
]