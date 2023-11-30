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
    obj = json.loads(request.body)
    username = obj.get('username', None)
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
    obj = json.loads(request.body)
    cid = obj.get('id', None)
    course = models.Course.objects.get(cid=cid)

    teachers = getTeachers(cid)
    tagsInfo = getTags(cid)

    revJsons = getReviews(cid)
    return JsonResponse({
        'id': cid,
        'name': course.name,
        'school': course.school,
        'teacher': teachers,
        'tag': tagsInfo,
        'reviews': revJsons
    })


def review(request):
    obj = json.loads(request.body)
    username = obj.get('username', None)
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
    obj = json.loads(request.body)
    rid = obj.get('id', None)
    username = obj.get('username', None)
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
        return JsonResponse({
            'ret': 1
        })
    else:
        return JsonResponse({
            'ret': 0
        })






