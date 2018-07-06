from rest_framework import serializers
from django_redis import get_redis_connection


class ImageCodeCheckSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        print(text)
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get('img_%s' % image_code_id).decode()
        print(real_image_code_text)
        redis_conn.delete('img_%s' % image_code_id, )
        if not real_image_code_text:
            raise serializers.ValidationError('验证码不存在')
        if real_image_code_text.lower() != text.lower():
            raise serializers.ValidationError('请输入正确的验证码')
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('sms_code_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('请求过于频繁')
        return attrs
