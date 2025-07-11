from django.shortcuts import render,HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import User, UserProfile

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

import json
import random
import re
import os
from django.conf import settings

# Create your views here.

def generate_verification_code():
    """生成6位数验证码"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

@csrf_exempt
def send_verification_code(request):
    """发送验证码"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            
            # 验证手机号
            if not validate_phone(phone):
                return JsonResponse({
                    'status': 'error', 
                    'message': '手机号格式不正确'
                }, status=400)
            
            # 检查手机号是否已注册
            if User.objects.filter(phone=phone).exists():
                return JsonResponse({
                    'status': 'error', 
                    'message': '该手机号已注册'
                }, status=400)
            
            # 生成验证码
            code = generate_verification_code()
            
            # TODO: 实际应用中接入短信服务发送验证码
            # 这里仅做模拟
            print(f"验证码发送成功：{code}")
            
            # 创建临时用户或保存验证码
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'username': phone,
                    'verification_code': code,
                    'verification_code_expires_at': timezone.now() + timezone.timedelta(minutes=10)
                }
            )
            
            if not created:
                user.verification_code = code
                user.verification_code_expires_at = timezone.now() + timezone.timedelta(minutes=10)
                user.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': '验证码发送成功'
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': '无效请求'}, status=405)

@csrf_exempt
def register(request):
    """用户注册"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            code = data.get('code')
            password = data.get('password')
            nickname = data.get('nickname', '')
            
            # 验证手机号和验证码
            try:
                user = User.objects.get(phone=phone)
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error', 
                    'message': '请先获取验证码'
                }, status=400)
            
            # 验证码校验
            if not user.is_verification_code_valid(code):
                return JsonResponse({
                    'status': 'error', 
                    'message': '验证码错误或已过期'
                }, status=400)
            
            # 设置用户信息
            user.set_password(password)
            user.nickname = nickname
            user.phone_verified = True
            user.verification_code = None
            user.verification_code_expires_at = None
            user.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': '注册成功',
                'user': {
                    'username': user.username,
                    'nickname': user.nickname
                }
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': '无效请求'}, status=405)

def index(request):
    return HttpResponse("_____")

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'status': 'success', 
                    'message': '登录成功',
                    'user': {
                        'username': user.username,
                        'nickname': user.nickname
                    }
                })
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': '用户名或密码错误'
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
    return JsonResponse({'status': 'error', 'message': '无效请求'}, status=405)

def user_logout(request):
    logout(request)
    return JsonResponse({'status': 'success', 'message': '注销成功'})


@api_view(['POST'])
@login_required
def update_profile(request):
    """更新头像和昵称"""
    user = request.user
    if request.method == 'POST':
        avatar = request.FILES.get('avatar', None)
        nickname = request.data.get('nickname', None)

        # 更新头像
        if avatar:
            user.avatar = avatar

        # 更新昵称
        if nickname:
            user.nickname = nickname

        user.save()  # 保存用户信息

        return Response({
            'status': 'success',
            'message': '个人资料更新成功',
            'user': {
                'username': user.username,
                'nickname': user.nickname,
                'avatar': user.avatar.url if user.avatar else None
            }
        }, status=status.HTTP_200_OK)

@csrf_exempt
@require_http_methods(["POST"])
def update_avatar(request):
    try:
        openid = request.POST.get('openid')
        avatar_file = request.FILES.get('avatar')

        if not openid or not avatar_file:
            return JsonResponse({'code': 400, 'message': '参数缺失'})

        # 获取用户信息
        user_profile, created = UserProfile.objects.get_or_create(openid=openid)

        # 删除旧头像
        if user_profile.avatar:
            old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(user_profile.avatar))
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)

        # 保存新头像
        user_profile.avatar = avatar_file
        user_profile.save()

        return JsonResponse({
            'code': 200,
            'message': '头像更新成功',
            'data': {
                'avatar_url': request.build_absolute_uri(user_profile.avatar.url)
            }
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def update_nickname(request):
    try:
        data = json.loads(request.body)
        openid = data.get('openid')
        nickname = data.get('nickname')

        if not openid or not nickname:
            return JsonResponse({'code': 400, 'message': '参数缺失'})

        # 获取用户信息
        user_profile, created = UserProfile.objects.get_or_create(openid=openid)
        user_profile.nickname = nickname
        user_profile.save()

        return JsonResponse({
            'code': 200,
            'message': '昵称更新成功',
            'data': {
                'nickname': nickname
            }
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)})

@require_http_methods(["GET"])
def get_user_info(request):
    try:
        openid = request.GET.get('openid')
        if not openid:
            return JsonResponse({'code': 400, 'message': '参数缺失'})

        user_profile = UserProfile.objects.get(openid=openid)
        avatar_url = request.build_absolute_uri(user_profile.avatar.url) if user_profile.avatar else ''

        return JsonResponse({
            'code': 200,
            'data': {
                'nickname': user_profile.nickname,
                'avatar_url': avatar_url
            }
        })
    except UserProfile.DoesNotExist:
        return JsonResponse({'code': 404, 'message': '用户不存在'})