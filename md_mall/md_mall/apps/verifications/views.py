from django.http import HttpResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.views import APIView
from md_mall.libs.captcha.captcha import captcha

# Create your views here.
from md_mall.apps.verifications import constants


class ImageCodeView(APIView):
    """
    图片验证码
    """
    def get(self, request, image_code_id):
        """
        获取图片验证码
        :param request:
        :param image_code_id:
        :return:
        """
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('img_%s'%image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type='image/jpg')