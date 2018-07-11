from .yuntongxun.sms import CCP
from celery_tasks.main import celery_app
# 发起任务

# 发送短信验证码
SMS_CODE_TENPLATE = 1

@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code, expire):
    '''
    发送短信验证码
    :return:
    '''
    # 发送短信
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, expire], SMS_CODE_TENPLATE)



