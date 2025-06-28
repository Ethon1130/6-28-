from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    # 扩展用户模型
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name='昵称')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    phone = models.CharField(max_length=11, unique=True, verbose_name='手机号', default='0000000000')
    phone_verified = models.BooleanField(default=False, verbose_name='手机号是否验证')
    verification_code = models.CharField(max_length=6, blank=True, null=True, verbose_name='验证码')
    verification_code_expires_at = models.DateTimeField(null=True, blank=True, verbose_name='验证码过期时间')
    nickname = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        
    def __str__(self):
        return self.username
    
    def is_verification_code_valid(self, code):
        """检查验证码是否有效"""
        if not self.verification_code:
            return False
        
        if self.verification_code != code:
            return False
        
        if timezone.now() > self.verification_code_expires_at:
            return False
        
        return True

class UserProfile(models.Model):
    openid = models.CharField(max_length=100, unique=True)
    nickname = models.CharField(max_length=50, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.openid
