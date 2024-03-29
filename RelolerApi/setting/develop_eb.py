from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'elasticbeanstalk.com',
    'relolerapi-env.eba-r394bymg.ap-northeast-2.elasticbeanstalk.com',
    '127.0.0.1',
    'localhost',
    ### EC2 private IP
    "172.31.34.104",
]

# CORS 세팅
# 찐배포에서는 CORS_ORIGIN_ALLOW_ALL = False, CORS_ALLOW_WHITELIST 이용
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True