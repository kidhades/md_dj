from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from md_mall.utils.QQ_login import oauth_qq
from md_mall.utils.exceptions import QQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer


class QQauth_url_view(APIView):
    """
    获取QQ登录的url
    """


    def get(self, request):
        """
        提供用于qq登录的url
        """
        next = request.query_params.get('next')
        print(next)
        oauth = oauth_qq(state=next)
        login_url = oauth.get_qq_login_url()
        return Response({'login_url': login_url})


class QQauth_token_view(CreateAPIView):
    serializer_class = OAuthQQUserSerializer
    def get(self, request):
        code = request.query_params.get('code')
        print(code)
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        oauth = oauth_qq()
        try:
            access_token = oauth.get_qq_login_access_token(code)
            # print('access_token')
            # print(access_token)
            openid = oauth.get_qq_login_openid(access_token)
            # print('openid')
            # print(openid)
        except QQAPIError:
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            token = oauth.generate_save_user_token(openid)
            print('token')
            print(token)
            return Response({'access_token': token})
        else:
            user = qq_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'access_token': token,
                'user_id': user.id,
                'username': user.username
            })
            print('access_token')
            print(token)
            return response
