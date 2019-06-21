import psycopg2
import boto3
import datetime
from botocore.exceptions import NoCredentialsError
from lxml.html import document_fromstring
from psycopg2.extensions import AsIs

def getKey():
    with open('myKeys.txt', 'r') as f:
        line = f.readline()
        map = line.strip().split(',')
    return map[0], map[1], map[2]

def extract_info_9anime(page):
    tree = document_fromstring(page)
    # import pdb; pdb.set_trace()
    a_name = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div/div[contains(@class, "info")]/div/div/h2/@data-jtitle')
    a_image = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div/div[contains(@class, "thumb")]/img/@src')
    a_genre = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div[@class = "row"]/div[contains(@class, "info")]/div[@class = "row"]/dl[1]/dd[5]/a/text()')
    a_rating = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div/div[contains(@class, "info")]/div/div[@class = "rating"]/@data-value')
    a_quality = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div[@class = "row"]/div[contains(@class, "info")]/div[@class = "row"]/dl[2]/dd[4]/span/text()')
    e_num = tree.xpath('//*[@id="servers-container"]/div/div[2]/div[1]/ul/li/a/@data-comment')
    e_href = tree.xpath('//*[@id="servers-container"]/div/div[2]/div[1]/ul/li/a/@href')
    # ['6 Angels']
    # ['https://static.akacdn.ru/files/images/2018/04/30396816148021f14209b6861167a601.jpg']
    # ['Action', 'Sci-Fi']
    # ['9.7']
    # ['SD']
    # ['1', '2', '3', '4', '5', '6']
    # ['/watch/6-angels.8p2q/95zk8n', '/watch/6-angels.8p2q/yxpn1j', '/watch/6-angels.8p2q/85zokq', '/watch/6-angels.8p2q/wvnl16', '/watch/6-angels.8p2q/x9omj8', '/watch/6-angels.8p2q/45zk2m']
    a_rows = [[a_name[0], a_image[0], 'NULL']]
    e_rows = []
    es = []
    for i in range(len(e_num)):
        es.append(['https://www1.9anime.nl'+ e_href[i], e_num[i], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    e_rows.append(es)
   # print(a_rows)
   # print(e_rows)
    return a_rows, e_rows

def extract_info_crunchyroll(page):
    tree = document_fromstring(page)
    a_rows = []
    e_rows = []
    a_img = tree.xpath('//ul[@id="sidebar_elements"]/li[1]/img/@src')
    # import pdb; pdb.set_trace()
    if tree.xpath('//div[@id="showview_content_videos"]/ul/li[@class="season small-margin-bottom"]'):
        # print('Multiple sessions')
        a_names = tree.xpath('//div[@id="showview_content_videos"]/ul/li[@class="season small-margin-bottom"]/a/@title')
        for i in range(len(a_names)):
            path = '//div[@id="showview_content_videos"]/ul/li[' + str(i+1) + ']'
            e_num = tree.xpath(path + '/ul/li/div/a/span/text()')
            e_href = tree.xpath(path + '/ul/li/div/a/@href')
            a = [a_names[i], a_img[0], 'NULL']
            es = []
            for j in range(len(e_num)):
                n = e_num[j].strip()
                start = n.find('Episode ')
                if start > -1:
                    n = n[start+8:]
                es.append(['https://www.crunchyroll.com'+e_href[j], n, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            a_rows.append(a)
            e_rows.append(es)
    else:
       # print('One session')
        a_name = tree.xpath('//div[@id="container"]/h1/span/text()')
        e_num = tree.xpath('//div[@id="showview_content_videos"]/ul/li[1]/ul[1]/li/div/a/span/text()')
        e_href = tree.xpath('//div[@id="showview_content_videos"]/ul/li[1]/ul[1]/li/div/a/@href')
        a = [a_name[0], a_img[0], 'NULL']
        es = []
        for j in range(len(e_num)):
            n = e_num[j].strip()
            start = n.find('Episode ')
            if start > -1:
                n = n[start+8:]
            es.append(['https://www.crunchyroll.com'+e_href[j], n, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        a_rows.append(a)
        e_rows.append(es)
        # print('============ %s ==========' % a_name)
        # print(a)
        # print(es)
    return a_rows, e_rows

def extract_info_kissanime(page):
    tree = document_fromstring(page)
    # import pdb; pdb.set_trace()
    a_name = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[1]/div[2]/div[2]/a/text()')
    a_image = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="rightside"]/div[1]/div[2]/div[2]/img/@src')
    a_genre = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[1]/div[2]/div[2]/p[2]/a/text()')
    e_num = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[@class="bigBarContainer"]/div[@class="barContent episodeList"]/div/table[@class="listing"]/tbody/tr/td[1]/a/text()')
    e_href = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[@class="bigBarContainer"]/div[@class="barContent episodeList"]/div/table[@class="listing"]/tbody/tr/td[1]/a/@href')
    a_rows = [[a_name[0], a_image[0], 'NULL']]
    e_rows = []
    es = []
    for i in range(len(e_num)):
        n = e_num[i].strip()
        start = n.find(' Episode ')
        if start > -1:
            n = n[start+9:]
        es.append(['https://kissanime.ru'+ e_href[i], n, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    e_rows.append(es)
   # print(a_rows)
   # print(e_rows)
    return a_rows, e_rows

def loadtoDB(rds, web_name, page):
    # load information in specific S3 file into DB
    if web_name == '9anime':
        a_rows, e_rows = extract_info_9anime(page)
    elif web_name == 'crunchyroll':
        a_rows, e_rows = extract_info_crunchyroll(page)
    elif web_name == 'kissanime':
        a_rows, e_rows = extract_info_kissanime(page)
    cur = rds.cursor()
    for i in range(len(a_rows)):
        a = a_rows[i]
        es = e_rows[i]
        a[0] = a[0].replace("'", "''")
        print(a[0])
        statement = "SELECT a_aid FROM anime WHERE a_atitle = '%s'"
        cur.execute(statement, (AsIs(a[0]),))
        row = cur.fetchone()
        if row is None:
            statement = "INSERT INTO anime(a_atitle, a_aimg, a_language) VALUES ('%s', %s, %s) RETURNING a_aid;"
            data = (AsIs(a[0]), a[1], AsIs(a[2]))
            cur.execute(statement, data)
            aid = cur.fetchone()[0]
            # ADD genre
        else:
            aid = row[0]
        statement = "SELECT w_wid FROM website WHERE w_wtitle = %s"
        cur.execute(statement, (web_name,))
        wid = cur.fetchone()[0]
        for e in es:
            statement = "INSERT INTO episode(e_aid, e_wid, e_eurl, e_enum, e_edate) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (e_aid, e_wid, e_enum) DO NOTHING;"
            data = (aid, wid, e[0], e[1], e[2])
            cur.execute(statement, data)
    rds.commit()

def load(web_name, date):
    start = datetime.datetime.now()
    # rdsect to S3
    ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
    bucketname = 'insightanimedata'
    s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    print('Connect to S3 successfully')

    # rdsect to database
    DB_NAME = 'animedb'
    USER_NAME = 'animelover'
    USER_PWD = 'atpx4869'
    HOST_NAME = 'yucheninstancedb.cucvespz1pxc.us-east-1.rds.amazonaws.com'
    PORT_NUM = 5432
    rds = psycopg2.connect(database=DB_NAME, user=USER_NAME, password=USER_PWD, host=HOST_NAME, port=PORT_NUM)
    print('Connect to PostgreSQL successfully')

    key = web_name+'/'+date+'/anime_pages/'
    response = s3.list_objects_v2(Bucket=bucketname,Prefix=key, MaxKeys = 20)

    if 'Contents' in response:
        # recursion for getting all bojects
        while response['KeyCount'] == 1000:
              for item in response['Contents']:
                  if item['Key'] == key:
                      continue
                  print(item['Key'])
                  obj = s3.get_object(Bucket=bucketname, Key=item['Key'])
                  page= obj['Body'].read()
                  print('inwhile')
                  loadtoDB(rds, web_name, page)
              response = s3.list_objects_v2(Bucket=bucketname, Prefix=key,StartAfter=item['Key'])
              print('----------- check key %s and count %d ----------------' % (item['Key'],  response['KeyCount']))
        for item in response['Contents']:
              if item['Key'] == key:
                  continue
              print(item['Key'])
              obj = s3.get_object(Bucket=bucketname, Key=item['Key'])
              page = obj['Body'].read()
              print('outwhile')
              loadtoDB(rds, web_name, page)
        end = datetime.datetime.now()
        print (start.strftime('Input into database starts at %Y-%m-%d %H:%M:%S'))
        print (end.strftime('Input into database ends at %Y-%m-%d %H:%M:%S'))
        print ('Process time = %s' % str(end - start))
    else:
        print('No such website or date')
    rds.close()

# load('9anime', 'init')

load('9anime', '2019-06-20')
# with open('../crawl_test/kissanime/ACCA_13-ku_Kansatsu-ka_(Dub).html', 'r') as f:
#     page = f.read()
#     extract_info_kissanime(page)
# with open('../crawl_test/crunchyroll/A_Bridge_to_the_Starry_Skies_-_Hoshizora_e_Kakaru_Hashi.html', 'r') as f:
#     page = f.read()
#     extract_info_crunchyroll(page)
# with open('../crawl_test/crunchyroll/A_Certain_Magical_Index.html', 'r') as f:
#     page = f.read()
#     extract_info_crunchyroll(page)
# with open('../crawl_test/9anime/6_Angels.html', 'r') as f:
#     page = f.read()
#     extract_info_9anime(page)
#ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
#bucketname = 'insightanimedata'
#s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
#print('Connect to S3 successfully')
#key = 'crunchyroll/init/anime_pages/'
#response = s3.list_objects_v2( Bucket=bucketname,  Prefix=key)
#if 'Contents' in response:
#    for item in response['Contents']:
#        print(item['Key'])
