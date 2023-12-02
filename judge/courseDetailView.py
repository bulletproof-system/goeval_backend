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

def collect(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyToken(token)
    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)

    obj = json.loads(request.body)
    username = getUserInfo(token).get('username')

    cid = obj.get('id', None)
    uid = models.User.objects.get(username=username).uid
    star = models.Star.objects.filter(user_id=uid, course_id=cid)
    if star.count() == 0:

        models.Star.objects.create(user_id=models.User.objects.get(uid=uid),
                                   course_id=models.Course.objects.get(cid=cid))
        return JsonResponse({
            'ret': 1
        })
    else:

        star[0].delete()
        return JsonResponse({
            'ret': 0
        })

def detail(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyToken(token)
    if authToken == FORMAT_TOKEN_ERROR:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)

    if authToken != NO_TOKEN_ERROR:
        username = getUserInfo(token).get('username')
    else:
        username = None
    if username is not None:
        uid = models.User.objects.get(username=username).uid
    else:
        uid = None
    obj = json.loads(request.body)
    cid = obj.get('id', None)
    course = models.Course.objects.get(cid=cid)

    teachers = getTeachers(cid)
    tagsInfo = getTags(cid)

    revJsons = getReviews(cid,uid)
    return JsonResponse({
        'id': cid,
        'name': course.name,
        'school': course.school,
        'teacher': teachers,
        'tag': tagsInfo,
        'description': course.description,
        'collected': collected(cid,uid),
        'reviews': revJsons
    })


def review(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyToken(token)
    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)



    obj = json.loads(request.body)
    username = getUserInfo(token).get('username')
    content = obj.get('content', None)
    rating = obj.get('rating', None)
    cid = obj.get('id', None)
    uid = models.User.objects.get(username=username).uid
    reviews = models.Review.objects.filter(user_id=uid, course_id=cid)
    if reviews.count() == 0:
        rid = genReviewId()
        models.Review.objects.create(
            rid=rid,
            content=content,
            date=datetime.now(),
            user_id=models.User.objects.get(uid=uid),
            course_id=models.Course.objects.get(cid=cid),
            rating=rating
        )
        nid = genNotificationId()
        models.NewReviewNotification.objects.create(
            nid=nid,
            content=models.Course.objects.get(cid=cid).name,
            date=datetime.now(),
            status=0,
            user_id=models.User.objects.get(username=username),
            review_id=models.Review.objects.get(rid=rid)
        )
        return JsonResponse({
            'ret': 1
        })
    else:
        return JsonResponse({
            'ret': 0
        })

def acqComments(request):

    obj = json.loads(request.body)
    rid = obj.get('id', None)
    comInfo = getComments(rid)
    return JsonResponse({
        'comments': comInfo
    })

def replyReview(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyToken(token)
    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)


    obj = json.loads(request.body)
    rid = obj.get('id', None)
    username = getUserInfo(token).get('username')
    content = obj.get('content', None)
    if rid and username and content:
        user = models.User.objects.get(username=username)
        cid = genCommentId()
        models.Comment.objects.create(
            cid=cid,
            content=content,
            date=datetime.now(),
            user_id=user,
            review_id=models.Review.objects.get(rid=rid)
        )

        nid = genNotificationId()
        models.NewCommentNotification.objects.create(
            nid=nid,
            content=content,
            date=datetime.now(),
            status=0,
            user_id=user,
            comment_id=models.Comment.objects.get(cid=cid)
        )
        return JsonResponse({
            'ret': 1
        })
    else:
        return JsonResponse({
            'ret': 0
        })


def like(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    authToken = verifyToken(token)
    if authToken != SUCCESS:
        return JsonResponse({'success': False,
                             'reason': 'TokenFail'
                             }, status=errorStatus)
    obj = json.loads(request.body)
    rid = obj.get('id', None)
    username = getUserInfo(token).get('username')
    uid = models.User.objects.get(username=username)
    likes = models.Like.objects.filter(user_id=uid, review_id=rid)
    if likes.count() > 0:
        like = likes[0]
        like.delete()
    else:
        models.Like.objects.create(
            user_id=models.User.objects.get(uid=uid),
            review_id=models.Review.objects.get(rid=rid)
        )
    return JsonResponse({
        'success': True
    })






