import boto3, os
__client = None

def initialize():
    print('INITIALIZING AWS....')
    __client = boto3.client('iot', region_name=os.environ['AWS_REGION'])
    print(os.environ['AWS_REGION'])
    return  __client