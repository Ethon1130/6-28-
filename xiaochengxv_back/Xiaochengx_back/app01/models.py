from django.db import models
from django.contrib.auth.models import AbstractUser
import os
import uuid

def user_avatar_path(instance, filename):
    # 为上传的头像生成唯一文件名
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('avatars', filename)

# Create your models here.

class User(AbstractUser):
    # 扩展用户模型
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name='昵称')
    avatar = models.ImageField(
        upload_to=user_avatar_path, 
        blank=True, 
        null=True, 
        verbose_name='头像',
        default='avatars/default.png'  # 默认头像
    )
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        
    def __str__(self):
        return self.username

    @property
    def avatar_url(self):
        # 如果没有头像，返回默认头像URL
        return self.avatar.url if self.avatar else '/media/avatars/default.png'
