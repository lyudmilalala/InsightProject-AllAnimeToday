import boto3
from botocore.exceptions import NoCredentialsError

def upload(filename, foldername):
    ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
    bucketname = 'insightanimedata'
    s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    # s3 = session.resource('s3')
    try:
        s3.upload_file(filename, bucketname, foldername+'/'+filename)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def getKey():
    with open('myKeys.txt', 'r') as f:
        line = f.readline()
        map = line.strip().split(',')
    return map[0], map[1], map[2]
