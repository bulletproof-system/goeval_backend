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
import math


def getUserList(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    page = obj.get('page', None)
    page_size = obj.get('page_size', None)

    all = models.User.objects.all().count()
    users = screenUser(obj)

    user_sum = len(users)
    actual_page = math.ceil(user_sum / page_size)
    if actual_page == 0:
        return JsonResponse({
            'all': all,
            'now': user_sum,
            'page_total': actual_page,
            'page': page,
            'userlist': []
        })

    if page > actual_page:
        page = actual_page

    if page == actual_page:
        page_users = users[page_size * (page - 1):]
    else:
        page_users = users[page_size * (page - 1): page_size * page]
    page_total = actual_page

    usersInfo = []
    for user in page_users:
        usersInfo.append(user.getUserInfo())

    return JsonResponse({
        'all': all,
        'now': user_sum,
        'page_total': page_total,
        'page': page,
        'userlist': usersInfo
    })


def deleteUser(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    uid = obj.get('uid', None)
    if uid is None:
        return MANAGER_INVAILD

    users = models.User.objects.filter(uid=uid)
    if users.count() == 0:
        return MANAGER_INVAILD

    user = users[0]
    if user.permission == 2:
        return JsonResponse({
            'success': False
        })

    user.delete()
    return JsonResponse({
        'success': True
    })


def modifyRole(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    uid = obj.get('uid', None)
    role = obj.get('role', None)
    if uid is None or role is None:
        return MANAGER_INVAILD

    users = models.User.objects.filter(uid=uid)
    if users.count() == 0:
        return MANAGER_INVAILD

    user = users[0]
    user.permission = role
    user.save()
    return JsonResponse({
        'success': True
    })


def modifyEmail(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    uid = obj.get('uid', None)
    email = obj.get('email', None)

    if uid is None or email is None:
        return MANAGER_INVAILD

    users = models.User.objects.filter(uid=uid)
    if users.count() == 0:
        return MANAGER_INVAILD

    if not isLegalEmail(email):
        return JsonResponse({
            'success': False,
            'reason': 'manage.user.operate.email.format'
        })

    user = users[0]
    user.email = email
    user.save()
    return JsonResponse({
        'success': True
    })


def modifyPasswd(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    uid = obj.get('uid', None)
    password = obj.get('password', None)

    if uid is None or password is None:
        return MANAGER_INVAILD

    users = models.User.objects.filter(uid=uid)
    if users.count() == 0:
        return MANAGER_INVAILD

    if not isLegalPW(password):
        return JsonResponse({
            'success': False,
            'reason': 'manage.user.operate.password.format'
        })

    user = users[0]
    user.password = password
    user.save()
    return JsonResponse({
        'success': True
    })


def acqCourse(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()
    obj = json.loads(request.body)
    page = obj.get('page', None)
    page_size = obj.get('page_size', None)
    all = models.Course.objects.all().count()
    courses = screenCourses(obj)
    total = len(courses)

    actual_page = math.ceil(total / page_size)
    if actual_page == 0:
        return JsonResponse({
            'all': all,
            'total': total,
            'page_total': actual_page,
            'page': page,
            'courselist': []
        })

    if page > actual_page:
        page = actual_page

    if page == actual_page:
        page_courses = courses[page_size * (page - 1):]
    else:
        page_courses = courses[page_size * (page - 1): page_size * page]

    print(page_courses)
    courseInfo = []
    for course in page_courses:
        courseInfo.append(getCourseInfo(course))

    return JsonResponse({
        'all': all,
        'total': total,
        'page_total': actual_page,
        'page': page,
        'courselist': courseInfo
    })


def deleteCourse(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()
    obj = json.loads(request.body)
    cid = obj.get('cid', None)

    if cid is None:
        return MANAGER_INVAILD

    courses = models.Course.objects.filter(cid=cid)

    if courses.count() == 0:
        return MANAGER_INVAILD

    course = courses[0]
    course.delete()

    return JsonResponse({
        'success': True
    })


def updateCourse(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()
    obj = json.loads(request.body)

    cid = obj.get('id', None)
    name = obj.get('name', None)
    school = obj.get('school', None)
    teachers = obj.get('teacher', None)
    tags = obj.get('tag', None)
    description = obj.get('description', None)

    if cid is None:
        return MANAGER_INVAILD

    courses = models.Course.objects.filter(cid=cid)

    if courses.count() == 0:
        return MANAGER_INVAILD

    course = courses[0]
    course.delete()
    models.Course.objects.create(
        cid=cid,
        school=school,
        name=name,
        description=description
    )
    course = models.Course.objects.get(cid=cid)
    for teacher in teachers:
        teacherItem = models.Teacher.objects.get(teacher_name=teacher)
        models.CourseTeacher.objects.create(
            course_id=course,
            teacher_id=teacherItem
        )

    for tag in tags:
        tagItem = models.Tag.objects.get(content=tag)
        models.TagCourse.objects.create(
            tag_id=tagItem,
            course_id=course
        )

    return JsonResponse({
        'success': True
    })


def addCourse(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()
    obj = json.loads(request.body)
    name = obj.get('name', None)
    school = obj.get('school', None)
    teachers = obj.get('teacher', None)
    tags = obj.get('tag', None)
    description = obj.get('description', None)

    cid = genCourseId()
    models.Course.objects.create(
        cid=cid,
        school=school,
        name=name,
        description=description
    )
    course = models.Course.objects.get(cid=cid)
    for teacher in teachers:
        teacherItem = models.Teacher.objects.get(teacher_name=teacher)
        models.CourseTeacher.objects.create(
            course_id=course,
            teacher_id=teacherItem
        )

    for tag in tags:
        tagItem = models.Tag.objects.get(content=tag)
        models.TagCourse.objects.create(
            tag_id=tagItem,
            course_id=course
        )

    return JsonResponse({
        'success': True
    })


def acqAnnouncement(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    page = obj.get('page', None)
    page_size = obj.get('page_size', None)
    all = models.Announcement.objects.all().count()
    select_announcements = screenAnnouncement(obj)

    total = len(select_announcements)

    actual_page = math.ceil(total / page_size)

    if actual_page == 0:
        return JsonResponse({
            'all': all,
            'total': 0,
            'page_total': actual_page,
            'page': page,
            'announcementlist': []
        })

    if page > actual_page:
        page = actual_page

    if page == actual_page:
        page_announcements = select_announcements[page_size * (page - 1):]
    else:
        page_announcements = select_announcements[page_size * (page - 1): page_size * page]

    announceInfo = []

    for announcement in page_announcements:
        announceInfo.append(announcement.getAnnInfo())

    return JsonResponse({
        'all': all,
        'total': total,
        'page_total': actual_page,
        'page': page,
        'announcementlist': announceInfo
    })


def deleteAnnouncement(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()
    obj = json.loads(request.body)
    aid = obj.get('aid', None)

    if aid is None:
        return MANAGER_INVAILD

    announcements = models.Announcement.objects.filter(aid=aid)

    if announcements.count() == 0:
        return MANAGER_INVAILD

    announcement = announcements[0]

    announcement.delete()

    return JsonResponse({
        'success': True
    })


def modifyAnnouncement(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    aid = obj.get('aid', None)
    title = obj.get('title', None)
    content = obj.get('content', None)

    if aid is None:
        return MANAGER_INVAILD

    announcements = models.Announcement.objects.filter(aid=aid)

    if announcements.count() == 0:
        return MANAGER_INVAILD

    announcement = announcements[0]

    announcement.title = title
    announcement.content = content

    announcement.save()

    return JsonResponse({
        'success': True
    })


def addAnnoucement(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    userInfo = getUserInfo(token)
    username = userInfo.get('username')
    user = models.User.objects.get(username=username)
    obj = json.loads(request.body)
    title = obj.get('title', None)
    content = obj.get('content', None)
    aid = genAnnouncementId()

    models.Announcement.objects.create(
        aid=aid,
        title=title,
        content=content,
        date=datetime.now(),
        user_id=user
    )

    return JsonResponse({
        'success': True
    })


def getTeacherList(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    teachers = models.Teacher.objects.all()
    teaInfo = []
    for teacher in teachers:
        teaInfo.append(teacher.teacher_name)

    return JsonResponse(teaInfo, safe=False)


def getTagsList(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    tags = models.Tag.objects.all()
    tagInfo = []
    for tag in tags:
        tagInfo.append(tag.content)

    return JsonResponse(tagInfo, safe=False)


def acqTeacher(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    page = obj.get('page', None)
    page_size = obj.get('page_size', None)
    all = models.Teacher.objects.all().count()
    select_teachers = screenTeacher(obj)

    total = len(select_teachers)

    actual_page = math.ceil(total / page_size)

    if actual_page == 0:
        return JsonResponse({
            'all': all,
            'total': 0,
            'page_total': actual_page,
            'page': page,
            'teacherlist': []
        })

    if page > actual_page:
        page = actual_page

    if page == actual_page:
        page_teachers = select_teachers[page_size * (page - 1):]
    else:
        page_teachers = select_teachers[page_size * (page - 1): page_size * page]

    teacherInfo = []

    for teacher in page_teachers:
        teacherInfo.append(teacher.getTeacherInfo())

    return JsonResponse({
        'all': all,
        'total': total,
        'page_total': actual_page,
        'page': page,
        'teacherlist': teacherInfo
    })


def deleteTeahcer(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    tid = obj.get('tid')

    if models.Teacher.objects.filter(tid=tid):
        teacher = models.Teacher.objects.get(tid=tid)
        teacher.delete()
        return JsonResponse({
            'success': True
        })
    else:
        return JsonResponse({
            'success': False
        })


def modifyTeacher(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)

    tid = obj.get('tid')
    name = obj.get('name')
    if tid is None:
        return JsonResponse({
            'success': False
        })

    if models.Teacher.objects.filter(tid=tid):
        teacher = models.Teacher.objects.get(tid=tid)
        teacher.teacher_name = name
        teacher.save()
        return JsonResponse({
            'success': True
        })
    else:
        return JsonResponse({
            'success': False
        })


def addTeacher(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)

    name = obj.get('name')
    if name is None:
        return JSON_FAIL

    tid = genTeacherId()

    models.Teacher.objects.create(
        tid=tid,
        teacher_name=name
    )

    return JSON_SUCCESS


def acqTags(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)
    page = obj.get('page', None)
    page_size = obj.get('page_size', None)
    all = models.Tag.objects.all().count()
    select_tags = screenTags(obj)

    total = len(select_tags)

    actual_page = math.ceil(total / page_size)

    if actual_page == 0:
        return JsonResponse({
            'all': all,
            'total': 0,
            'page_total': actual_page,
            'page': page,
            'taglist': []
        })

    if page > actual_page:
        page = actual_page

    if page == actual_page:
        page_tags = select_tags[page_size * (page - 1):]
    else:
        page_tags = select_tags[page_size * (page - 1): page_size * page]

    tagInfo = []

    for tag in page_tags:
        tagInfo.append(tag.getInfo())

    return JsonResponse({
        'all': all,
        'total': total,
        'page_total': actual_page,
        'page': page,
        'taglist': tagInfo
    })


def deleleTag(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)

    tid = obj.get('tid')
    if tid is None:
        return JSON_FAIL

    if models.Tag.objects.filter(tid=tid):
        tag = models.Tag.objects.get(tid=tid)
        tag.delete()
        return JSON_SUCCESS
    else:
        return JSON_FAIL


def modifyTag(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)

    tid = obj.get('tid')
    name = obj.get('name')

    if tid is None:
        return JSON_FAIL

    if models.Tag.objects.filter(tid=tid):
        tag = models.Tag.objects.get(tid=tid)
        tag.content = name
        tag.save()
        return JSON_SUCCESS
    else:
        return JSON_FAIL


def addTag(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyManager(token)
    if authToken != MANAGER_AUTH:
        return returnAuthError()

    obj = json.loads(request.body)

    name = obj.get('name')

    if name is None:
        return JSON_FAIL

    tid = genTagId()

    models.Tag.objects.create(
        tid=tid,
        content=name
    )
    return JSON_SUCCESS
