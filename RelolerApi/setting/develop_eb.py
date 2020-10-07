from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'elasticbeanstalk.com',
    'relolerapi-env.eba-r394bymg.ap-northeast-2.elasticbeanstalk.com',
    '127.0.0.1',
    'localhost',
    ### Elastic Load Balancer private IP
    '172.31.1.60',
    '172.31.46.248'
]