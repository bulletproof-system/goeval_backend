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

PIC_DIR = 'http://47.93.249.150/asset/image/'
#
# BASE_DIR = '.\\judge\\asset\\image\\'
BASE_DIR = '/asset/image'
DEFAULT_AVATAR_VISITOR = 'http://dummyimage.com/100x100/FF0000/000000&text=Visitor'
DEFAULT_AVATAR_USER = 'https://dummyimage.com/100x100/00FF00/000000&text=User'
manager = 2
normalUser = 1
visitor = 0
managerEmail = '1728901409@qq.com'
# DEFAULT_AVATAR = 'http://dummyimage.com/100x100/FF0000/000000&text=Visitor
# '


READ = 0
UNREAD = 1

errorStatus = 401
successStatus = 200

reviewNotification = 0
commentNotification = 1

MAX_REVIEW_NUM = 10000

FILE_MAX_SIZE = 2 * 1024 * 1024  # 2MB

MANAGER_INVAILD = JsonResponse({
    'success': False,
    'reason': 'manage.invalid'
})

JSON_SUCCESS = JsonResponse({
    'success': True
})

JSON_FAIL = JsonResponse({
    'success': False
})


def genReviewId():
    rids = models.Review.objects.all().order_by('-rid')
    if len(rids) == 0:
        return 1
    return rids[0].rid + 1


def genCommentId():
    cids = models.Comment.objects.all().order_by('-cid')
    if len(cids) == 0:
        return 1
    return cids[0].cid + 1


def genTeacherId():
    teachers = models.Teacher.objects.all().order_by('-tid')
    if len(teachers) == 0:
        return 1

    return teachers[0].tid + 1


def genCourseId():
    courses = models.Course.objects.all().order_by('-cid')
    if len(courses) == 0:
        return 1
    return courses[0].cid + 1


def genAnnouncementId():
    announcements = models.Announcement.objects.all().order_by('-aid')
    if len(announcements) == 0:
        return 1
    return announcements[0].aid + 1


def genNotificationId():
    notifications = models.Notification.objects.all().order_by('-nid')
    if len(notifications) == 0:
        return 1
    return notifications[0].nid + 1


def genTagId():
    tags = models.Tag.objects.all().order_by('-tid')
    if len(tags) == 0:
        return 1
    return tags[0].tid + 1


def getTeachers(cid):
    coTes = models.CourseTeacher.objects.filter(course_id=cid)
    teachers = []
    for coTe in coTes:
        teacher_id = coTe.teacher_id
        teacher = models.Teacher.objects.get(tid=teacher_id)
        teachers.append(teacher.teacher_name)
    return teachers


def getTags(cid):
    tagCourses = models.TagCourse.objects.filter(course_id=cid)
    tagsInfo = []
    for tagC in tagCourses:
        tag_id = tagC.tag_id
        tag = models.Tag.objects.get(tid=tag_id)
        tagsInfo.append(tag.content)
    return tagsInfo


def getReviews(cid, uid):
    reviews = models.Review.objects.filter(course_id=cid)
    revJsons = []
    for review in reviews:
        user_id = review.user_id
        user = models.User.objects.get(uid=user_id)
        count = models.Like.objects.filter(review_id=review.rid).count()
        liked = False
        if models.Like.objects.filter(review_id=review.rid, user_id=uid):
            liked = True
        revJsons.append({
            'id': review.rid,
            'username': user.username,
            'avatar': user.avatar,
            'datetime': review.date,
            'content': review.content,
            'rating': review.rating,
            'count': count,
            'liked': liked
        })
    return revJsons


def check_string(re_exp, str):
    res = re.search(re_exp, str)
    if res:
        return True
    else:
        return False


def isLegalEmail(email):
    return check_string('^[a-z0-9A-Z]+[- | a-z0-9A-Z . _]+@([a-z0-9A-Z]+(-[a-z0-9A-Z]+)?\\.)+[a-z]{2,}$', email)


def isLegalPW(password):
    if len(password) <= 20 and len(password) >= 6:
        return True
    return False


def isLegalUN(username):
    if len(username) <= 20 and len(username) >= 3:
        return True
    return False


FILE_REG = '^[^\s\.]*\.(jpeg|png|gif|jpg)'


def isLegalAvatar(pic_name):
    return check_string(FILE_REG, pic_name)


NO_TOKEN_ERROR = 0
FORMAT_TOKEN_ERROR = 1
NO_USER_ERROR = 2
OVER_TIME_ERROR = 3
NO_AUTH_ERROR = 4
MANAGER_AUTH = 5

SUCCESS = 6


def returnAuthError():
    return JsonResponse({
        'success': False,
        'reason': 'your auth is too low'
    }, status=401)


def verifyManager(token):
    if len(token) == 0:
        return NO_TOKEN_ERROR

    token = token.split()[1]
    # 如果解析错误那么返回游客信息
    try:
        userInfo = jwt.decode(token,
                              "secret",
                              algorithms=["HS256"],
                              headers=headers)
    except:
        return FORMAT_TOKEN_ERROR

    username = userInfo.get("username")
    lastLoginTime = userInfo.get("logintime")
    # 不存在这个人也返回token信息
    if not models.User.objects.filter(username=username):
        return NO_USER_ERROR

    nowTime = datetime.now();
    lastTime = datetime.strptime(lastLoginTime, "%Y-%m-%d %H:%M:%S")
    timeDelta = nowTime - lastTime
    gapSeconds = timeDelta.seconds
    if (gapSeconds >= 60 * 60 * 2):
        return OVER_TIME_ERROR

    user = models.User.objects.get(username=username)
    if user.permission == 0:
        return NO_AUTH_ERROR
    if user.permission == 2:
        return MANAGER_AUTH
    return SUCCESS


def verifyToken(token):
    if len(token) == 0:
        return NO_TOKEN_ERROR

    token = token.split()
    if len(token) < 2:
        return NO_TOKEN_ERROR
    # 如果解析错误那么返回游客信息
    token = token[1]
    try:
        userInfo = jwt.decode(token,
                              "secret",
                              algorithms=["HS256"],
                              headers=headers)
    except:
        return FORMAT_TOKEN_ERROR

    username = userInfo.get("username")
    lastLoginTime = userInfo.get("logintime")
    # 不存在这个人也返回token信息
    if not models.User.objects.filter(username=username):
        return NO_USER_ERROR

    nowTime = datetime.now();
    lastTime = datetime.strptime(lastLoginTime, "%Y-%m-%d %H:%M:%S")
    timeDelta = nowTime - lastTime
    gapSeconds = timeDelta.seconds
    if (gapSeconds >= 60 * 60 * 2):
        return OVER_TIME_ERROR

    user = models.User.objects.get(username=username)
    if user.permission == 0:
        return NO_AUTH_ERROR

    return SUCCESS


def getUserInfo(token):
    token = token.split()[1]
    userInfo = jwt.decode(token,
                          "secret",
                          algorithms=["HS256"],
                          headers=headers)
    return userInfo


def getUserStarList(user_id):
    starList = models.Star.objects.filter(user_id=user_id)
    starInfo = []
    for star in starList:
        course_id = star.course_id.cid
        course = models.Course.objects.get(cid=course_id)
        teachers = getTeachers(course_id)
        tags = getTags(course_id)
        starInfo.append({
            'id': course_id,
            'name': course.name,
            'school': course.school,
            'teacher': teachers,
            'tag': tags,
            'description': course.description
        })

    return starInfo


def getComments(rid):
    comments = models.Comment.objects.filter(review_id=rid)
    comInfo = []
    for comment in comments:
        username = comment.user_id.username
        avatar = comment.user_id.avatar
        comInfo.append({
            'id': comment.cid,
            'username': username,
            'avatar': avatar,
            'datetime': comment.date,
            'content': comment.content
        })
    return comInfo


def screenUser(obj):
    uid = obj.get('uid', None)
    username = obj.get('username', None)
    email = obj.get('email', None)
    role = obj.get('role', None)
    users = models.User.objects.all()
    if uid is not None and len(str(uid)):
        newUsers = []
        for user in users:
            if str(uid) in str(user.uid):
                newUsers.append(user)
        users = newUsers

    if username is not None and len(username):
        newUsers = []
        for user in users:
            if username in user.username:
                newUsers.append(user)
        users = newUsers

    if email is not None and len(email):
        newUsers = []
        for user in users:
            if email in user.email:
                newUsers.append(user)
        users = newUsers

    if role is not None and len(str(role)):
        newUsers = []
        for user in users:
            if role == user.permission:
                newUsers.append(user)
        users = newUsers
    return users


def screenCourses(obj):
    cid = obj.get('cid', None)
    name = obj.get('name', None)
    school = obj.get('school', None)
    teacher = obj.get('teacher', None)
    tag = obj.get('tag', None)
    courses = models.Course.objects.all()

    if cid is not None and len(str(cid)):
        newCourses = []
        for course in courses:
            if str(cid) in str(course.cid):
                newCourses.append(course)
        courses = newCourses
    if name is not None and len(name):
        newCourses = []
        for course in courses:
            if name in course.name:
                newCourses.append(course)
        courses = newCourses

    if school is not None and len(school):
        newCourses = []
        for course in courses:
            if school in course.school:
                newCourses.append(course)
        courses = newCourses

    if teacher is not None and len(teacher):
        newCourses = []
        for course in courses:
            teachers = getTeachers(course.cid)
            for item in teachers:
                if teacher in item:
                    newCourses.append(course)
                    break
        courses = newCourses

    if tag is not None and len(tag):
        newCourses = []
        for course in courses:
            tags = getTags(course.cid)
            for item in tags:
                print(tag)
                if tag in item:
                    newCourses.append(course)
                    break
        courses = newCourses

    return courses


MAXMUM = 6


def seaCourses(obj):
    cid = obj.get('cid', None)
    name = obj.get('name', None)
    school = obj.get('school', None)
    teacher = obj.get('teacher', None)
    tag = obj.get('tag', None)
    if cid is None and name is None and school is None and teacher is None and tag is None:
        return models.Course.objects.all()
    courses = models.Course.objects.all()

    count = 0
    newCourses = []
    if cid is not None and len(str(cid)):

        for course in courses:
            if str(cid) in str(course.cid) and count < MAXMUM:
                newCourses.append(course)
                count = count + 1

    count = 0
    if name is not None and len(name):
        for course in courses:
            if name in course.name and count < MAXMUM:
                newCourses.append(course)
                count = count + 1

    count = 0
    if school is not None and len(school):
        for course in courses:
            if school in course.school and count < MAXMUM:
                newCourses.append(course)
                count = count + 1

    count = 0
    if teacher is not None and len(teacher):
        for course in courses:
            if count < MAXMUM:
                teachers = getTeachers(course.cid)
                for item in teachers:
                    if teacher in item:
                        newCourses.append(course)
                        count = count + 1
                        break

    count = 0
    if tag is not None and len(tag):
        for course in courses:
            if count < MAXMUM:
                tags = getTags(course.cid)
                for item in tags:
                    if tag in item:
                        newCourses.append(course)
                        count = count + 1
                        break

    return newCourses


def screenAnnouncement(obj):
    aid = obj.get('aid', None)
    title = obj.get('title', None)
    content = obj.get('content', None)

    announcements = models.Announcement.objects.all()

    if aid is not None and len(str(aid)):
        newAnnounces = []
        for announcement in announcements:
            if str(aid) in str(announcement.aid):
                newAnnounces.append(announcement)
        announcements = newAnnounces
    if title is not None and len(title):
        newAnnounces = []
        for announcement in announcements:
            if title in announcement.title:
                newAnnounces.append(announcement)
        announcements = newAnnounces

    if content is not None and len(content):
        newAnnounces = []
        for announcement in announcements:
            if content in announcement.content:
                newAnnounces.append(announcement)
        announcements = newAnnounces

    return announcements


def screenTeacher(obj):
    tid = obj.get('tid', None)
    name = obj.get('name', None)

    teachers = models.Teacher.objects.all()

    if tid is not None and len(str(tid)):
        newTeachers = []
        for teacher in teachers:
            if str(tid) in str(teacher.tid):
                newTeachers.append(teacher)

        teachers = newTeachers

    if name is not None and len(name):
        newTeachers = []
        for teacher in teachers:
            if name in teacher.teacher_name:
                newTeachers.append(teacher)
        teachers = newTeachers

    return teachers


def screenTags(obj):
    tid = obj.get('tid', None)
    name = obj.get('name', None)

    tags = models.Tag.objects.all()

    if tid is not None and len(str(tid)):
        newTags = []
        for tag in tags:
            if str(tid) in str(tag.tid):
                newTags.append(tag)

        tags = newTags

    if name is not None and len(name):
        newTags = []
        for tag in tags:
            if name in tag.teacher_name:
                newTags.append(tag)
        tags = newTags

    return tags


def getCourseInfo(course):
    return {
        'id': course.cid,
        'name': course.name,
        'school': course.school,
        'teacher': getTeachers(course.cid),
        'tag': getTags(course.cid),
        'description': course.description
    }


def collected(cid, uid):
    if cid is None or uid is None:
        return False

    if models.Star.objects.filter(user_id=uid, course_id=cid):
        return True
    else:
        return False
