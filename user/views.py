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


# class LoginView(View):
#     def get(self,request):
#         return HttpResponse("hello world!!")
#
#     def post(self,request):
#         if request.methods == 'POST':
#             print(request.POST)
#             print(request.body)
#             data = request.body.decode("ytf-8")
#             print("data",data)
#             json_data = json.loads(data)
#             print("json_data",json_data)
#             user_name = json_data.get("username")
#             print(user_name)

def index(request):
    obj = json.loads(request.body)  #这里有问题
    print(request.body)
    username = obj.get('username', None)
    password = obj.get('password', None)
    print(username)
    print(password)
    if username is None or password is None:
        return JsonResponse({'code': 404, 'message': '参数错误'})


    is_login = authenticate(request, username=username, password=password)
    print(is_login)
    if is_login is None:
        return JsonResponse({'code': 500, 'message': '账号或密码错误'})


    login(request, is_login)
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(is_login)
    token = jwt_encode_handler(payload)

    return JsonResponse({'success':True, 'token': token, 'userInfo':
        {'userName': username, 'avatar': 'ok', 'email': '3462515832@qq.com', 'role':1}})


# 下面的3个装饰器全部来自from引用，相当与给接口增加了用户权限校验和token校验
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@authentication_classes((JSONWebTokenAuthentication,))
def get_info(request):
    data = 'some info'
    return JsonResponse({'code': 200, 'message': '请求成功', 'data': data})
