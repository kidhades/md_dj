import logging
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen

from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from rest_framework.utils import json

from md_mall.utils import constants
from .exceptions import QQAPIError
from md_mall.settings import dev

logger = logging.getLogger('django')



class oauth_qq(object):
    """
    QQ认证辅助工具类
    """

    def __init__(self, state=None, client_id=None, redirect_uri=None,client_secret=None):
        self.state = state or dev.QQ_STATE
        self.client_id = client_id or dev.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri or dev.QQ_REDIRECT_URI
        self.client_secret = client_secret or dev.QQ_CLIENT_SECRET

    def get_qq_login_url(self):
        """
        获取qq登录的网址
        :return: url网址
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }

        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        # print(url)
        return url

    def get_qq_login_access_token(self, code):
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'client_secret': self.client_secret,
            'code': code,
        }
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        data = parse_qs(urlopen(url).read().decode())
        access_token = data.get('access_token', None)
        if not access_token:
            logger.error('code-%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIError

        return access_token[0]

    def get_qq_login_openid(self, access_token):
        params = {
            'access_token': access_token,
        }
        url = 'https://graph.qq.com/oauth2.0/me?' + urlencode(params)
        response = urlopen(url)
        print(222222222222)
        print(response)
        print(222222222222)
        response_data = response.read().decode()
        print(111111111111)
        print(response_data)
        print(111111111111)
        try:
            data = json.loads(response_data[10:-4])
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIError
        openid = data.get('openid', None)
        return openid

    @staticmethod
    def generate_save_user_token(openid):
        """
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: token
        """
        ser = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        data = {'openid': openid}
        token = ser.dumps(data)
        return token.decode()

    @staticmethod
    def check_save_user_token(token):
        """
        检验保存用户数据的token
        :param token: token
        :return: openid or None
        """
        ser = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        try:
            data = ser.loads(token)
        except BadData:
            return None
        else:
            return data.get('openid')
