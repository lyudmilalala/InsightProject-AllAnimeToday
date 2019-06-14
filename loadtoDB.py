import psycopg2
import boto3
import crawling
from botocore.exceptions import NoCredentialsError
from lxml.html import document_fromstring

def getKey():
    with open('myKeys.txt', 'r') as f:
        line = f.readline()
        map = line.strip().split(',')
    return map[0], map[1], map[2]

def extract_info_9anime(page):
    tree = document_fromstring(page)
    a_name = tree.xpath('//*[@id="main"]/div/div[9]/div/div[1]/div[2]/div[1]/div[1]/h2/@data-jtitle')
    a_image = tree.xpath('//*[@id="main"]/div/div[9]/div/div[1]/div[1]/img/src')
    a_type = tree.xpath('//*[@id="main"]/div/div[9]/div/div[1]/div[2]/div[3]/dl[1]/dd[5]/a/text()')
    a_rating = tree.xpath('//*[@id="main"]/div/div[9]/div/div[1]/div[2]/div[3]/dl[2]/dd[2]/span[1]/text()')
    a_quality = tree.xpath('//*[@id="main"]/div/div[9]/div/div[1]/div[2]/div[3]/dl[2]/dd[4]/span/text()')
    e_num = tree.xpath('//*[@id="servers-container"]/div/div[2]/div[1]/ul/li/a/@data-comment')
    e_href = tree.xpath('//*[@id="servers-container"]/div/div[2]/div[1]/ul/li/a/@href')
    print(a_name)
    print(a_image)
    print(a_type)
    print(a_rating)
    print(a_quality)
    print(e_num)
    print(e_href)
    # for e in elist:
    #
    #     e_temp = e.xpath('.//a')
    #     e_id = e_temp.get_attribute('data-comment')
    #     e_href = e_temp.get_attribute('href')
    #     e_info = [title, e_id, e_href]
    #     episodes.append(e_info)
    return 0

def extract_info_crunchyroll():
    return 0

def extract_info_kissanime():
    return 0

def load_9anime(s3, rds, bucketname, key):
    files = s3.list_objects_v2( Bucket=bucketname,  Prefix=key)
    if 'Contents' in response:
        for item in response['Contents']:
            page = item['Body'].read()
            a_row, e_rows = extract_info_9anime(page)
        # with open('animate.csv', 'w') as f:
        #     writer = csv.writer(f)
        #     for row in animates:
        #         writer.writerow(row)
    return a_row, e_rows

def load_crunchyroll(s3, rds, bucketname, key):
    return 0

def load_kissanime(s3, rds, bucketname, key):
    return 0

def loadtoDB(web_name, date):
    # rdsect to S3
    ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
    bucketname = 'insightanimedata'
    s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    print('rdsect to S3 successfully')
    # rdsect to database
    DB_NAME = 'animedb'
    USER_NAME = 'animelover'
    USER_PWD = 'atpx4869'
    HOST_NAME = 'yucheninstancedb.cucvespz1pxc.us-east-1.rds.amazonaws.com'
    PORT_NUM = 5432
    rds = psycopg2.rdsect(database=DB_NAME, user=USER_NAME, password=USER_PWD, host=HOST_NAME, port=PORT_NUM)
    print('rdsect to PostgreSQL successfully')
    key = web_name+'/'+date+'/anime_pages/'
    files = s3.list_objects_v2( Bucket=bucketname,  Prefix=key)
    if files:
        # load information in specific S3 file into DB
        if web_name == '9anime':
            load_9anime(s3, rds, bucketname, key)
        elif web_name == 'crunchyroll':
            load_crunchyroll(s3, rds, bucketname, key)
        elif web_name == 'kissanime':
            load_kissanime(s3, rds, bucketname, key)
        # add more website
    else:
        print('No such website or date')
    rds.close()

with open('crawl_test/9anime/6_Angels.html', 'r') as f:
    page = f.read()
    extract_info_9anime(page)
