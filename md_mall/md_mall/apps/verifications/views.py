import random

from rest_framework.response import Response

from md_mall.libs.yuntongxun.sms import CCP
from django.http import HttpResponse
# from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.views import APIView
from md_mall.libs.captcha.captcha import captcha
from rest_framework.generics import GenericAPIView
from md_mall.apps.verifications import constants
from .serializers import ImageCodeCheckSerializer

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

class SMSCodeView(GenericAPIView):
    serializer_class = ImageCodeCheckSerializer
    def get(self, request, mobile):
        ser = self.get_serializer(data=request.query_params)
        ser.is_valid(raise_exception=True)

        sms_code = random.randint(0, 999999)
        sms_code = '%06d'%sms_code

        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex('sms_code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)


        sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code,sms_code_expires], constants.SMS_CODE_TEMP_ID)
        return Response({'message':'ok'})