from django.shortcuts import render

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



def Login(request):
    obj = json.loads(request.body)  # 这里有问题

    print(request.body)
    uid = obj.get('uid', None)
    password = obj.get('password', None)
    print(uid)
    print(password)
    if uid is None or password is None:
        return JsonResponse({'code': 404, 'message': '参数错误'})
    print(models.User.objects.all())
    try:

        user = models.User.objects.get(uid = uid)
        print(user)
    except:
        return JsonResponse({'code': 404, 'message': '用户不存在'})

    if user.password != password:
        return JsonResponse({'code': 500, 'message': '账号或密码错误'})

    if user is None:
        return JsonResponse({'code': 500, 'message': '账号或密码错误'})

    login(request, user)
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    return JsonResponse({'success': True, 'token': token, 'userInfo':
        {'userName': user.username, 'avatar': 'ok', 'email': '3462515832@qq.com', 'role': 1}})


def Register(request):
    obj = json.loads(request.body)
    uid = obj.get('uid',None)
    username = obj.get('username',None)
    password = obj.get('password',None)
    email = obj.get('email',None)
    avatar = obj.get('avatar', None)
    permission = 0
    if avatar is None:
        avatar = "default"
    if uid is None or username is None or password is None or email is None:
        return JsonResponse({'code': 404, 'massage':'非法输入'})
    
    if models.User.objects.filter(uid = uid):
        return JsonResponse({'code': 500,'massage':'该用户已存在'})
    models.User.objects.create(uid = uid, username = username, password = password, email = email, avatar = avatar,permission = permission)
    user = models.User.objects.get(uid = uid)

    login(request, user)
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)

    return JsonResponse({'code': 200, 'success': True, 'token': token,
                         'userInfo':{'username': username, 'email': email, 'role': 0}})


# 下面的3个装饰器全部来自from引用，相当与给接口增加了用户权限校验和token校验
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def get_info(request):
    data = 'some info'
    return JsonResponse({'code': 200, 'message': '请求成功', 'data': data})
