from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    mobile = models.CharField(max_length=11, unique=True, verbose_name='mobile')

    class Meta:
        db_table = 'tb_users'
        verbose_name = 'user'
        verbose_name_plural = verbose_name