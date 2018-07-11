from celery import Celery


# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'md_mall.settings.dev'


# 创建celery对象
celery_app = Celery('md')

# 调用配置能文件
celery_app.config_from_object('celery_tasks.config')

# 接受发送的任务
#
celery_app.autodiscover_tasks(['celery_tasks.sms'])



