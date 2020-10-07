from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'elasticbeanstalk.com',
    'relolerapi-env.eba-r394bymg.ap-northeast-2.elasticbeanstalk.com',
    '127.0.0.1',
    'localhost',
    ### Elastic Load Balancer private IP
]

def get_elb_private_ips():
    import boto3
    import secret_keys
    try:
        elb = boto3.client('elbv2', 
            region_name = 'ap-northeast-2', 
            aws_access_key_id = secret_keys.aws_secret['AWS']['Access Key ID'],
            aws_secret_access_key = secret_keys.aws_secret['AWS']['Security Access Key']
        )
        ec2 = boto3.resource(service_name = 'ec2',
            region_name = 'ap-northeast-2',
            aws_access_key_id = secret_keys.aws_secret['AWS']['Access Key ID'],
            aws_secret_access_key = secret_keys.aws_secret['AWS']['Security Access Key']
        )
        lbs = []
        
        # 모든 로드 밸런서 가져오기
        for i in elb.describe_load_balancers()['LoadBalancers']:
            print(i)
            arn_index = i['LoadBalancerArn'].find('awseb-AWSEB')
            print(arn_index)
            if arn_index >= 0:
                lbs.append(i['LoadBalancerArn'][arn_index:])
        
        print(lbs)
        private_ips = []
        # 로드 밸런서에 맞는 네트워크 인터페이스 선별
        for i in ec2.network_interfaces.all():
            if True in map(lambda x: x in i.description, lbs):
                private_ips.append(i.private_ip_address)
        return private_ips
    except Exception:
        return []

ALLOWED_HOSTS += get_elb_private_ips()