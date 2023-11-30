from django.urls import path

from . import views, courseDetailView, managerView
MANAGER_VIEW_PREFIX = 'manage/'
MANAGER_VIEW_USER_PREFIX = 'manage/user/'
MANAGER_VIEW_COURSE_PREFIX = 'manage/course/'
MANAGER_VIEW_ANNOUNCEMENT_PREFIX = 'manage/announcement/'
urlpatterns = [
    path('login', views.Login, name='Login'),
    path('register',views.Register, name = 'Register'),
    path('getInfo',views.get_info, name = 'getInfo'),
    path('recommend', views.recCourse, name = 'recommend'),
    path('search', views.seaCourse, name = 'search'),
    path('autocomplete', views.autocomplete, name = 'autocomplete'),

    path('announcement', views.acqAnnouncement, name = 'announcement'),
    path('notification', views.acqNotification, name = 'notification'),
    path('read', views.signRead, name = 'read'),
    path('operate/email', views.changeEmail, name = 'operate/email'),
    path('operate/password', views.changePassword, name = 'operate/password'),
    path('operate/upload', views.uploadAvatar, name='operate/upload'),
    path('starlist', views.getStarList, name='starlist'),


#课程详情
    path('detail', courseDetailView.detail, name = 'detail'),
    path('collect',courseDetailView.collect, name='collect'),
    path('review', courseDetailView.review),
    path('comments', courseDetailView.acqComments),
    path('reply', courseDetailView.replyReview),

#管理员界面
    path(MANAGER_VIEW_USER_PREFIX + 'list', managerView.getUserList),
    path(MANAGER_VIEW_USER_PREFIX + 'delete', managerView.deleteUser),
    path(MANAGER_VIEW_USER_PREFIX + 'set', managerView.modifyRole),
    path(MANAGER_VIEW_USER_PREFIX + 'email', managerView.modifyEmail),
    path(MANAGER_VIEW_USER_PREFIX + 'password', managerView.modifyPasswd),

    path(MANAGER_VIEW_COURSE_PREFIX + 'list', managerView.acqCourse),
    path(MANAGER_VIEW_COURSE_PREFIX + 'delete', managerView.deleteCourse),
    path(MANAGER_VIEW_COURSE_PREFIX + 'edit', managerView.updateCourse),
    path(MANAGER_VIEW_COURSE_PREFIX + 'add', managerView.addCourse),

    path(MANAGER_VIEW_ANNOUNCEMENT_PREFIX + 'list', managerView.acqAnnouncement),
    path(MANAGER_VIEW_ANNOUNCEMENT_PREFIX + 'delete', managerView.deleteAnnouncement),
    path(MANAGER_VIEW_ANNOUNCEMENT_PREFIX + 'edit', managerView.modifyAnnouncement),
    path(MANAGER_VIEW_ANNOUNCEMENT_PREFIX + 'add', managerView.addAnnoucement),
]