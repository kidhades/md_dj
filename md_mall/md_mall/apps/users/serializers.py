import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from users.models import User


# class CreateUserSerializer(serializers.ModelSerializer):
#     # print(super())
#     password2 = serializers.CharField(label='password2', write_only=True)
#     sms_code = serializers.CharField(label='sms_code', write_only=True)
#     allow = serializers.CharField(label='allow?', write_only=True)
#
#     class Meta:
#
#         model = User
#         fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow')
#         extra_kwargs = {
#             'username': {
#                 'min_length': 5,
#                 'max_length': 20,
#                 'error_messages': {
#                     'min_length': '仅允许5-20个字符的用户名',
#                     'max_length': '仅允许5-20个字符的用户名',
#                 }
#             },
#             'password': {
#                 'write_only': True,
#                 'min_length': 8,
#                 'max_length': 20,
#                 'error_messages': {
#                     'min_length': '仅允许8-20个字符的密码',
#                     'max_length': '仅允许8-20个字符的密码',
#                 }
#             }
#         }
#
#         def validate_mobile(self, value):
#             """验证手机号"""
#             print(value)
#             if not re.match(r'^1[3-9]\d{9}$', value):
#                 raise serializers.ValidationError('手机号格式错误')
#             return value
#
#         def validate_allow(self, value):
#             """验证是否同意"""
#             print(value)
#             if value != 'true':
#                 raise serializers.ValidationError('需要同意')
#             return value
#
#         def validate(self, data):
#             print(data['password'])
#             print(data['password2'])
#             if data['password'] != data['password2']:
#                 raise serializers.ValidationError('密码不一致')
#             redis_conn = get_redis_connection('verify_codes')
#             mobile = data['mobile']
#             real_sms_code = redis_conn.get('sms_code_%s' % mobile)
#             if not real_sms_code:
#                 raise serializers.ValidationError('code不存在')
#             if real_sms_code.decode() != data['sms_code']:
#                 raise serializers.ValidationError('验证码输入错误')
#
#             return data
#
#         def create(self, validated_data):
#             del validated_data['password2']
#             del validated_data['allow']
#             del validated_data['sms_code']
#
#             user = super().create(validated_data)
#
#             user.set_password(validated_data['password'])
#             user.save()
#
#             return user
#

class CreateUserSerializer(serializers.ModelSerializer):
    """
    创建用户序列化器
    """
    token = serializers.CharField(label='token', read_only=True)
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_code_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    def create(self, validated_data):
        """
        创建用户
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user = super().create(validated_data)

        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()
        return instance