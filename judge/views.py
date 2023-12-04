import shutil

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
from .func import *
import os
from PIL import Image
from django.core.files.storage import FileSystemStorage


def Login(request):
    obj = json.loads(request.body)  # 这里有问题
    username = obj.get('username', None)
    password = obj.get('password', None)
    if username is None or password is None:
        return JsonResponse({
            'success': False,
            'reason': 'login.error.format'})
    try:
        user = models.User.objects.get(username=username)
    except:
        return JsonResponse({
            'success': False,
            'reason': 'login.error.auth'})

    if user.password != password:
        return JsonResponse({
            'success': False,
            'reason': 'login.error.auth'
        })

    if user is None:
        return JsonResponse({
            'success': False,
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

    return JsonResponse({
        'success': True,
        'info':
            {'token': token,
             'userInfo':
                 {'username': username,
                  'avatar': user.avatar,
                  'email': user.email,
                  'role': user.permission}
             }
    })


def Register(request):
    obj = json.loads(request.body)
    username = obj.get('username', None)
    password = obj.get('password', None)
    email = obj.get('email', None)
    uid = random.randint(1, 10000)
    while models.User.objects.filter(uid=uid).exists():
        uid = random.randint(1, 10000)

    avatar = DEFAULT_AVATAR_USER
    permission = normalUser

    if uid is None or not isLegalUN(username) or not isLegalPW(password):
        return JsonResponse({
            'success': False,
            'info': None,
            'reason': 'register.error.format'
        })

    if models.User.objects.filter(username=username):
        return JsonResponse({
            'success': False,
            'info': None,
            'reason': 'register.error.samename'
        })
    models.User.objects.create(uid=uid,
                               username=username,
                               password=password,
                               email=email,
                               avatar=avatar,
                               permission=permission)

    token = jwt.encode({"username": username,
                        "logintime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        },
                       "secret",
                       algorithm="HS256",
                       headers=headers).decode('ascii')

    return JsonResponse({
        'success': True,
        'info': {
            'token': token,
            'userInfo':
                {'username': username,
                 'avatar': avatar,
                 'email': email,
                 'role': permission
                 }
        },
        'reason': None
    })


# 下面的3个装饰器全部来自from引用，相当与给接口增加了用户权限校验和token校验

def get_info(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyToken(token)
    # 没有提供token  那么也返回游客信息
    if authToken == NO_TOKEN_ERROR:
        return JsonResponse({'username': 'Visitor',
                             'avatar': 'http://dummyimage.com/100x100/FF0000/000000&text=Visitor',
                             'role': 0
                             })

    # 如果解析错误那么返回游客信息
    if authToken == FORMAT_TOKEN_ERROR:
        return JsonResponse({'username': 'Visitor',
                             'avatar': 'http://dummyimage.com/100x100/FF0000/000000&text=Visitor',
                             'role': 0
                             })

    # 不存在这个人也返回token信息
    if authToken == NO_USER_ERROR:
        return JsonResponse({'username': 'Visitor',
                             'avatar': 'http://dummyimage.com/100x100/FF0000/000000&text=Visitor',
                             'role': 0
                             })

    if authToken == OVER_TIME_ERROR:
        return JsonResponse({
            'reason': 'getInfo.error.overtime'
        }, status=errorStatus)

    userInfo = getUserInfo(token)

    username = userInfo.get("username")
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
            teachers = getTeachers(cid)
            tagsInfo = getTags(cid)
            res.append({'id': course.cid,
                        'name': course.name,
                        'school': course.school,
                        'teacher': teachers,
                        'tag': tagsInfo})
        return JsonResponse(res, safe=False)

    if num > 20:
        num = 20
    top = models.Course.objects.all().count()
    select = random.sample(range(0, top - 1), num)
    for rand in select:
        course = models.Course.objects.all()[rand]
        cid = course.cid
        teachers = getTeachers(cid)
        tagsInfo = getTags(cid)
        res.append({'id': course.cid,
                    'name': course.name,
                    'school': course.school,
                    'teacher': teachers,
                    'tag': tagsInfo})

    return JsonResponse(res, safe=False)


def seaCourse(request):
    obj = json.loads(request.body)
    key = obj.get('key', None)

    res = []
    search = {
        'cid': key,
        'name': key,
        'school': key,
        'teacher': key,
        'tag': key
    }
    courses = screenCourses(search)

    for course in courses:
        cid = course.cid
        teachers = getTeachers(cid)
        tagsInfo = getTags(cid)
        res.append({'id': course.cid,
                    'name': course.name,
                    'school': course.school,
                    'teacher': teachers,
                    'tag': tagsInfo})

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
                'type': 0,
                'value': name
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
        if key in teacher_name:
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


def acqNotification(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyToken(token)

    if authToken == NO_TOKEN_ERROR:
        return JsonResponse([],safe=False)

    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)

    userInfo = getUserInfo(token)
    username = userInfo.get("username")
    user = models.User.objects.get(username=username)
    notifications = models.NewReviewNotification.objects.filter(user_id=user.uid)
    resInfo = []
    for notification in notifications:
        nid = notification.nid
        datetime = notification.date
        status = notification.status
        review = notification.review_id
        course = review.course_id
        course_name = course.name
        ntype = reviewNotification
        resInfo.append({
            'nid': nid,
            'course_id': course.cid,
            'course_name': course_name,
            'review_id': review.rid,
            'datetime': datetime,
            'status': status,
            'ntype': ntype
        })

    notifications = models.NewCommentNotification.objects.filter(user_id=user.uid)
    for notification in notifications:
        nid = notification.nid
        datetime = notification.date
        status = notification.status
        comment = notification.comment_id
        review = comment.review_id
        course = review.course_id
        course_name = course.name
        ntype = commentNotification
        resInfo.append({
            'nid': nid,
            'course_id': course.cid,
            'course_name': course_name,
            'review_id': review.rid,
            'comment_id': comment.cid,
            'datetime': datetime,
            'status': status,
            'ntype': ntype
        })

    # data = json.loads(resInfo)
    # sorted_data = sorted(data, cmp=lambda x, y: (
    #     x[datetime] < y[datetime] if x[status] == y[status] else y[status] - x[status]))
    return JsonResponse(resInfo, safe=False)


def signRead(request):
    token = request.META.get('HTTP_AUTHORIZATION')

    authToken = verifyToken(token)
    if authToken != SUCCESS:
        return JsonResponse({'success': False
                             },
                            status=errorStatus)

    obj = json.loads(request.body)
    nid = obj.get('nid', None)

    if nid is None:
        return JsonResponse({'success': False
                             },
                            status=errorStatus)

    notification = models.Notification.objects.get(nid=nid)
    if notification.nid != READ:
        notification.status = READ
        notification.save()
    return JsonResponse({
        'success': True
    })


def changePassword(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyToken(token)
    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)

    obj = json.loads(request.body)
    oldPassword = obj.get('oldPassword', None)
    newPassword = obj.get('newPassword', None)

    userInfo = getUserInfo(token)

    username = userInfo.get("username")
    user = models.User.objects.get(username=username)
    password = user.password

    if not isLegalPW(oldPassword) or password != oldPassword:
        return JsonResponse({'success': False,
                             'reason': 'userInfo.operate.password.auth'
                             }, status=successStatus)

    if not isLegalPW(newPassword):
        return JsonResponse({'success': False,
                             'reason': 'userInfo.operate.password.format'
                             }, status=successStatus)

    user.password = newPassword
    user.save()
    return JsonResponse({
        'success': True,
        'reason': 'correct'
    })


def changeEmail(request):
    token = request.META.get('HTTP_AUTHORIZATION')

    authToken = verifyToken(token)
    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)

    obj = json.loads(request.body)
    email = obj.get('email', None)
    if not isLegalEmail(email):
        return JsonResponse({
            'success': False,
            'reason': 'userInfo.operate.email.format'

        })

    userInfo = getUserInfo(token)
    username = userInfo.get("username")
    user = models.User.objects.get(username=username)
    user.email = email
    user.save()
    return JsonResponse({
        'success': True,
        'reason': 'correct'
    })


def uploadAvatar(request):
    token = request.META.get('HTTP_AUTHORIZATION')

    authToken = verifyToken(token)
    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    username = getUserInfo(token).get('username')
    user = models.User.objects.get(username=username)
    pic = request.FILES["file"]
    pic_name = pic.name
    if not isLegalAvatar(pic_name):
        return JsonResponse({'success': False,
                             'reason': 'userInfo.operate.avatar.type'
                             })

    if pic.size > FILE_MAX_SIZE:
        return JsonResponse({'success': False,
                             'reason': 'userInfo.operate.avatar.size'
                             })

    suffix = '.' + pic_name.split('.')[1]
    path_file = os.path.join(BASE_DIR, str(user.uid) + suffix)
    if os.path.exists(path_file):
        os.remove(path_file)
    FileSystemStorage(location=BASE_DIR).save(str(user.uid) + suffix, pic)
    user.avatar = PIC_DIR + str(user.uid) + suffix
    user.save()
    return JsonResponse({
        'success': True,
        'avatar': PIC_DIR + str(user.uid) + suffix
    })


def getStarList(request):
    token = request.META.get('HTTP_AUTHORIZATION')

    authToken = verifyToken(token)

    if authToken == NO_TOKEN_ERROR or authToken == NO_AUTH_ERROR:
        return JsonResponse({})

    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)

    userInfo = getUserInfo(token)
    username = userInfo.get('username')
    user_id = models.User.objects.get(username=username).uid
    starList = getUserStarList(user_id)

    return JsonResponse(starList, safe=False)
