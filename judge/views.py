import jwt
from django.shortcuts import render
import re
# Create your views here.
from django.http import HttpResponse
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from . import models
import time
from datetime import datetime
import random


headers = {
    'alg': "HS256",
}


def Login(request):
    obj = json.loads(request.body)  # 这里有问题
    username = obj.get('username', None)
    password = obj.get('password', None)
    if username is None or password is None:
        return JsonResponse({'code': 200,
                             'success':False,
                             'Info':None,
                             'reason': 'login.error.format'})
    try:

        user = models.User.objects.get(username = username)
    except:
        return JsonResponse({'code': 200,
                             'success': False,
                             'Info': None,
                             'reason': 'login.error.auth'})

    if user.password != password:
        return  JsonResponse({'code': 200,
                              'success': False,
                              'Info': None,
                              'reason': 'login.error.auth'
                              })

    if user is None:
        return JsonResponse({'code': 200,
                             'success': False,
                             'Info': None,
                             'reason': 'login.error.auth'
                             })

    # login(request, user)
    # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    # payload = jwt_payload_handler(user)
    # token = jwt_encode_handler(payload)
    token = jwt.encode({"username": username,
                        "logintime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        },
                       "secret",
                       algorithm="HS256",
                       headers=headers).decode('ascii')

    return JsonResponse({'code': 200,
                         'success': True,
                         'Info':
                             {'token': token,
                              'userinfo':
                                  {'username': username,
                                   'avatar': user.avatar,
                                   'email': user.email,
                                   'role' : user.permission}
                              }
                         })


def Register(request):
    obj = json.loads(request.body)
    username = obj.get('username', None)
    password = obj.get('password', None)
    uid = random.randint(1,10000)
    while models.User.objects.filter(uid = uid).exists():
        uid = random.randint(1,10000)

    avatar = 'cute tiger'
    permission = 0
    email = 'default'
    if avatar is None:
        avatar = "default"
    if uid is None or username is None or password is None:
        return JsonResponse({'code': 200,
                             'success': False,
                             'Info': None,
                             'reason': 'register.error.format'
                             })
    
    if models.User.objects.filter(username = username):
        return JsonResponse({'code': 200,
                             'success': False,
                             'Info': None,
                             'reason': 'register.error.samename'
                             })
    models.User.objects.create(uid = uid,
                               username = username,
                               password = password,
                               email = email,
                               avatar = avatar,
                               permission = permission)

    token = jwt.encode({"username": username,
                        "logintime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        },
                       "secret",
                       algorithm="HS256",
                       headers=headers).decode('ascii')


    return JsonResponse({'code': 200,
                         'success': True,
                         'Info':{
                             'token': token,
                             'userinfo':
                                 {'username': username,
                                  'avatar': avatar,
                                  'email': email,
                                  'role': 0
                                  }
                         },
                          'reason': None
                         })


# 下面的3个装饰器全部来自from引用，相当与给接口增加了用户权限校验和token校验

def get_info(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    userInfo = jwt.decode(token,
                          "secret",
                          algorithms=["HS256"],
                          headers=headers)
    username = userInfo.get("username")
    lastLoginTime = userInfo.get("logintime")
    if not models.User.objects.filter(username=username):
        return JsonResponse({'code': 401,
                             'reason': 'getInfo.error.dontexsitsuser'
                             })

    nowTime = datetime.now();
    lastTime = datetime.strptime(lastLoginTime, "%Y-%m-%d %H:%M:%S")
    timeDelta = nowTime - lastTime
    gapSeconds = timeDelta.seconds
    if(gapSeconds >= 60 * 60 * 2):
        return JsonResponse({'code': 401,
                             'reason': 'getInfo.error.overtime'
                             })

    user = models.User.objects.filter(username=username)[0]
    return JsonResponse({'username': username,
                         'avatar': user.avatar,
                         'email': user.email,
                         'role': user.permission
                         })



def recCourse(request):
    obj = json.loads(request.body)
    num = obj.get('num', None)
    if num is None:
        num = 20
    res = []
    if num >= models.Course.objects.all().count():
        courses = models.Course.objects.all()
        for course in courses:
            cid = course.cid
            coTes = models.CourseTeacher.objects.filter(course_id = cid)
            teachers = []
            for coTe in coTes:
                teacher_id = coTe.teacher_id
                teacher = models.Teacher.objects.get(teacher_name = teacher_id)
                teachers.append(teacher.teacher_name)
            res.append({'id': str(course.cid),
                        'name': course.name,
                        'school': course.school,
                        'teacher': teachers})
        return JsonResponse(res, safe=False)

    select = []
    if num > 20:
        num = 20
    top = models.Course.objects.all().count()
    while select.count() == num:
        rand = random.randint(0, top - 1)
        if rand not in select:
            course = models.Course.objects.all()[rand]
            res.append({'id': str(course.cid),
                        'name': course.name,
                        'school': course.school,
                        'teacher': []})

    return JsonResponse(res, safe=False)


def seaCourse(request):
    obj = json.loads(request.body)
    key = obj.get('key', None)
    courses = models.Course.objects.all()
    res = []
    for course in courses :
        cid = str(course.cid)
        name = course.name
        school = course.school
        set = cid + name + school
        if key in set:
            cid = course.cid
            coTes = models.CourseTeacher.objects.filter(course_id=cid)
            teachers = []
            for coTe in coTes:
                teacher_id = coTe.teacher_id
                teacher = models.Teacher.objects.get(teacher_name=teacher_id)
                teachers.append(teacher.teacher_name)
            res.append({'id': str(course.cid),
                        'name': course.name,
                        'school': course.school,
                        'teacher': teachers})

    return JsonResponse(res, safe=False)





def autocomplete(request):
    obj = json.loads(request.body)
    key = obj.get('key', None)
    res = []
    courses = models.Course.objects.all()
    for course in courses:
        name = course.name
        if key in name:
            res.append({
                'type' : 0,
                'value' : name
            })
        school = course.school
        if key in school:
            res.append({
                'type': 1,
                'value': school
            })
    teachers = models.Teacher.objects.all()
    for teacher in teachers:
        teacher_name = teacher.teacher_name
        if key in  teacher_name:
            res.append({
                'type': 2,
                'value': teacher_name
            })

    tags = models.Tag.objects.all()
    for tag in tags:
        content = tag.content
        if key in content:
            res.append({
                'type': 3,
                'value': content
            })

    return JsonResponse(res, safe=False)



def detail(request):
    obj = json.loads(request.body)
    cid = obj.get('id', None)
    course = models.Course.objects.get(cid = cid)
    coTes = models.CourseTeacher.objects.filter(course_id=cid)
    teachers = []
    for coTe in coTes:
        teacher_id = coTe.teacher_id
        teacher = models.Teacher.objects.get(teacher_name=teacher_id)
        teachers.append(teacher.teacher_name)

    reviews = models.Review.objects.filter(course_id = cid)
    revJsons = []
    for review in reviews:
        user_id = review.user_id
        user = models.User.objects.get(uid = user_id)
        revJsons.append({
            'username': user.username,
            'avatar': user.avatar,
            'datetime': review.date,
            'content': review.content,
            'rating': review.rating
        })

    return JsonResponse({
        'id': cid,
        'name': course.name,
        'school': course.school,
        'teacher': teachers,
        'reviews': revJsons
    })



def acqAnnouncement(request):
    announcements = []
    for announcement in models.Announcement.objects.all():
        announcements.append({
            'aid': announcement.aid,
            'title': announcement.title,
            'content': announcement.content,
            'datetime': announcement.date
        })

    return JsonResponse(announcements, safe=False)



# def acqNotification(request):
#
#
#
def signRead(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    obj = json.loads(request.body)
    nid = obj.get('nid', None)
    userInfo = jwt.decode(token,
                          "secret",
                          algorithms=["HS256"],
                          headers=headers)
    username = userInfo.get("username")

    lastLoginTime = userInfo.get("logintime")
    if not models.User.objects.filter(username=username):
        return JsonResponse({'success': False,
                             'reason': 'userInfo.read.dont.exists.user'
                             })

    nowTime = datetime.now();
    lastTime = datetime.strptime(lastLoginTime, "%Y-%m-%d %H:%M:%S")
    timeDelta = nowTime - lastTime
    gapSeconds = timeDelta.seconds
    if (gapSeconds >= 60 * 60 * 2):
        return JsonResponse({'success': False,
                             'reason': 'userInfo.read.overtime'
                             })

    notification = models.Notification.objects.get(nid = nid)
    notification.status = 1
    notification.save()
    return JsonResponse({
        'success': "True"
    })

def changePassword(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    obj = json.loads(request.body)
    oldPassword = obj.get('oldPassword', None)
    newPassword = obj.get('newPassword', None)
    userInfo = jwt.decode(token,
                          "secret",
                          algorithms=["HS256"],
                          headers=headers)
    username = userInfo.get("username")

    lastLoginTime = userInfo.get("logintime")
    if not models.User.objects.filter(username=username):
        return JsonResponse({'success': False,
                             'reason': 'userInfo.operate.password.dont.exists.user'
                             })

    nowTime = datetime.now();
    lastTime = datetime.strptime(lastLoginTime, "%Y-%m-%d %H:%M:%S")
    timeDelta = nowTime - lastTime
    gapSeconds = timeDelta.seconds
    if (gapSeconds >= 60 * 60 * 2):
        return JsonResponse({'success': False,
                             'reason': 'userInfo.operate.password.overtime'
                             })
    user = models.User.objects.get(username=username)
    password = user.password
    if password != oldPassword:
        return JsonResponse({'success': False,
                             'reason': 'userInfo.operate.password.wrong.password'
                             })

    user.password = newPassword
    user.save()
    return JsonResponse({
        'success': True,
        'reason': 'correct'
    })

def check_string(re_exp, str):
    res = re.search(re_exp, str)
    if res:
        return True
    else:
        return False

def changeEmail(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    obj = json.loads(request.body)
    email = obj.get('email', None)
    if not check_string('^[a-z0-9A-Z]+[- | a-z0-9A-Z . _]+@([a-z0-9A-Z]+(-[a-z0-9A-Z]+)?\\.)+[a-z]{2,}$',email):
        return JsonResponse({
            'success': False,
            'reason': 'userInfo.operate.email.format'

        })

    userInfo = jwt.decode(token,
                          "secret",
                          algorithms=["HS256"],
                          headers=headers)
    username = userInfo.get("username")

    lastLoginTime = userInfo.get("logintime")
    if not models.User.objects.filter(username=username):
        return JsonResponse({'success': 401,
                             'reason': 'userInfo.operate.email.error.dontexsitsuser'
                             })

    nowTime = datetime.now();
    lastTime = datetime.strptime(lastLoginTime, "%Y-%m-%d %H:%M:%S")
    timeDelta = nowTime - lastTime
    gapSeconds = timeDelta.seconds
    if(gapSeconds >= 60 * 60 * 2):
        return JsonResponse({'success': 401,
                             'reason': 'userInfo.operate.email.error.overtime'
                             })

    user = models.User.objects.get(username=username)
    user.email = email
    user.save()
    return JsonResponse({
        'success': True,
        'reason': 'correct'
    })




