import psycopg2
import boto3
import datetime
import re
import botocore
from botocore.exceptions import NoCredentialsError
from lxml.html import document_fromstring
from psycopg2.extensions import AsIs
import threading

def getKey():
    with open('../myKeys.txt', 'r') as f:
        line = f.readline()
        map = line.strip().split(',')
    return map[0], map[1], map[2]

def aname_cleaning(aname, ltype='(sub)'):
    # modify to the same lower and upper cases
    aname = aname.strip()
    aname = ' '.join(aname.split())
    aname = aname.lower()
    # modify synomyms by regular expression
    aname = aname.replace('2nd season', 'season 2')
    aname = aname.replace('season 2', '2')
    aname = aname.replace('3rd season', 'season 3')
    aname = aname.replace('season 3', '3')
    p1list = re.findall('\d+th season',aname)
    p2list = re.findall('season \d+',aname)
    if len(p1list) > 0:
        pos1 = aname.find(p1list[0])
        temp = p1list[0].find('th season')
        num1 = p1list[0][0:temp]
        aname = aname.replace(p1list[0], num1, 1)
    elif len(p2list) > 0:
        pos2 = aname.find(p2list[0])
        num2 = aname[pos2+7:pos2+len(p2list[0])]
        aname = aname.replace(p2list[0], num2, 1)
    # attach Dub and Sub to all titles to distinguish
    aname = aname.replace('(dubbed)', '(dub)')
    aname = aname.replace('(subtitled)', '(sub)')
    if aname.find('(dub)')<0 and aname.find('(sub)')<0:
        aname = aname + ' '+ ltype
    # recapitalize the name of anime to make it looks like a title
    aname = aname.title()
    return aname;

def enum_cleaning(enum):
    # distinguish numerical episodes and movies/SPs
    # eliminate leading zeros
    n = enum.strip()
    start = n.find('Episode')
    if start > -1:
        n = n[start+7:]
        n = n.strip()
    start = n.find('Preview')
    if start > -1:
        n = n[start:]
        n = n.strip()
    list = re.findall('\d+\.\d+|\d+', n)
    if len(list) > 0:
        n0 = list[0]
        n1 = n0.lstrip('0')
        n = n.replace(n0, n1, 1)
    return n;

def extract_info_9anime(page):
    tree = document_fromstring(page)
    # import pdb; pdb.set_trace()
    a_name_1 = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div/div[contains(@class, "info")]/div/div[@class = "c1"]/h2/text()')
    a_name_2 = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div/div[contains(@class, "info")]/div/div[@class = "c1"]/p/text()')
    a_img = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div/div[contains(@class, "thumb")]/img/@src')
    a_type = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div[@class = "row"]/div[contains(@class, "info")]/div[@class = "row"]/dl[1]/dd[1]/text()')
    a_genre = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div[@class = "row"]/div[contains(@class, "info")]/div[@class = "row"]/dl[1]/dd[5]/a/text()')
    a_rating = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div/div[contains(@class, "info")]/div/div[@class = "rating"]/@data-value')
    a_quality = tree.xpath('//div[contains(@class, "info")]/div[@class = "widget-body"]/div[@class = "row"]/div[contains(@class, "info")]/div[@class = "row"]/dl[2]/dd[4]/span/text()')
    e_num = tree.xpath('//*[@id="servers-container"]/div/div[2]/div[1]/ul/li/a/@data-comment')
    e_href = tree.xpath('//*[@id="servers-container"]/div/div[2]/div[1]/ul/li/a/@href')
    # ['6 Angels']
    # ['https://static.akacdn.ru/files/images/2018/04/30396816148021f14209b6861167a601.jpg']
    # ['TV Serie']
    # print(a_name_2)
    # ['Action', 'Sci-Fi']
    # ['9.7']
    # ['SD']
    # ['1', '2', '3', '4', '5', '6']
    # ['/watch/6-angels.8p2q/95zk8n', '/watch/6-angels.8p2q/yxpn1j', '/watch/6-angels.8p2q/85zokq', '/watch/6-angels.8p2q/wvnl16', '/watch/6-angels.8p2q/x9omj8', '/watch/6-angels.8p2q/45zk2m']
    if ( len(a_name_1) == 0 and len(a_name_2) == 0 ) or a_type[0] =='Movie':
        return [], []
    aname = []
    lt = '(sub)'
    aname.append(aname_cleaning(a_name_1[0]))
    if aname[0].find('(Dub)') > -1:
        lt = '(dub)'
    elif aname[0].find('(Sub)') > -1:
        lt = '(sub)'
    if len(a_name_2) != 0:
        if a_name_2[0] != '':
            names = a_name_2[0].split('; ')
            for n in range(len(names)):
                an = aname_cleaning(names[n], lt)
                if an != aname[0]:
                    aname.append(an)
    a_rows = [[aname, a_img[0]]]
    e_rows = []
    es = []
    for i in range(len(e_num)):
        e = enum_cleaning(e_num[i])
        es.append(['https://www1.9anime.nl'+ e_href[i], e, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
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
        # print('Multiple seasons')
        a_names = tree.xpath('//div[@id="showview_content_videos"]/ul/li[@class="season small-margin-bottom"]/a/@title')
        for i in range(len(a_names)):
            path = '//div[@id="showview_content_videos"]/ul/li[' + str(i+1) + ']'
            e_num = tree.xpath(path + '/ul/li/div/a/span/text()')
            e_href = tree.xpath(path + '/ul/li/div/a/@href')
            if len(a_names[i]) == 0:
                continue
            aname = aname_cleaning(a_names[i])
            a = [[aname], a_img[0]]
            es = []
            for j in range(len(e_num)):
                n = enum_cleaning(e_num[j])
                es.append(['https://www.crunchyroll.com'+e_href[j], n, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            a_rows.append(a)
            e_rows.append(es)
    else:
       # print('One session')
        a_name = tree.xpath('//div[@id="container"]/h1/span/text()')
        e_num = tree.xpath('//div[@id="showview_content_videos"]/ul/li[1]/ul[1]/li/div/a/span/text()')
        e_href = tree.xpath('//div[@id="showview_content_videos"]/ul/li[1]/ul[1]/li/div/a/@href')
        if len(a_name) == 0:
            return [], []
        aname = aname_cleaning(a_name[0])
        a = [[aname], a_img[0]]
        es = []
        for j in range(len(e_num)):
            n = enum_cleaning(e_num[j])
            es.append(['https://www.crunchyroll.com'+e_href[j], n, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        a_rows.append(a)
        e_rows.append(es)
    # print(a_rows)
    return a_rows, e_rows

def extract_info_kissanime(page):
    tree = document_fromstring(page)
    # import pdb; pdb.set_trace()
    a_name_1 = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[1]/div[2]/div[2]/a/text()')
    a_img = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="rightside"]/div[1]/div[2]/div[2]/img/@src')
    name_2_tag = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[1]/div[2]/div[2]/p[1]/span/text()')
    a_name_2 = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[1]/div[2]/div[2]/p[1]/a/text()')
    a_genre = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[1]/div[2]/div[2]/p[2]/a/text()')
    e_num = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[@class="bigBarContainer"]/div[@class="barContent episodeList"]/div/table[@class="listing"]/tbody/tr/td[1]/a/text()')
    e_href = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[@class="bigBarContainer"]/div[@class="barContent episodeList"]/div/table[@class="listing"]/tbody/tr/td[1]/a/@href')
    # print(a_name_1)
    # print(a_genre)
    # print(a_name_2)
    if ( len(a_name_1) == 0 and len(a_name_2) == 0 ) or 'Movie' in a_genre:
        return [], []
    if name_2_tag[0] == 'Genres':
        a_genre = a_name_2
    if name_2_tag[0] != 'Other name':
        a_name_2 = []
    aname = []
    lt = '(sub)'
    aname.append(aname_cleaning(a_name_1[0]))
    if aname[0].find('(Dub)') > -1:
        lt = '(dub)'
    elif aname[0].find('(Sub)') > -1:
        lt = '(sub)'
    for n in range(len(a_name_2)):
        n = aname_cleaning(a_name_2[n], lt)
        if n != aname[0]:
            aname.append(n)
    a_rows = [[aname, a_img[0]]]
    e_rows = []
    es = []
    for i in range(len(e_num)):
        n = enum_cleaning(e_num[i])
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
        aid = -1
        a = a_rows[i]
        es = e_rows[i]
        names = a[0]
        # print(a[0])
        statement = "SELECT an_aid FROM a_names WHERE "
        for n in range(len(names)):
            temp = names[n].replace("'", "''")
            statement = statement + "an_atitle = '"+ temp + "' OR "
        statement = statement[:-4] + ";"
        # print(statement)
        cur.execute(statement)
        row = cur.fetchone()
        if row is None:
            statement = "INSERT INTO anime(a_aimg) VALUES (%s) RETURNING a_aid;"
            cur.execute(statement, (a[1],))
            aid = cur.fetchone()[0]
            # for n in range(len(names)):
            #     statement = "INSERT INTO a_names(an_aid, an_atitle) VALUES (%s, %s) ON CONFLICT (an_atitle) DO NOTHING;"
            #     data = (aid, names[n])
            #     cur.execute(statement, data)
            # ADD genre
        else:
            aid = row[0]
            # insert the nicknames that are not already in the database into it
            # statement = "SELECT an_aname FROM a_names WHERE an_aid ="+aid;
            # cur.execute(statement)
            # rows = cur.fetchall()
            # print('---existing names---')
            # print(rows)
            # for r in rows:
            #     if r[0] in names:
            #         names.remove(r[0])
        for n in range(len(names)):
            statement = "INSERT INTO a_names(an_aid, an_atitle) VALUES (%s, %s) ON CONFLICT (an_atitle) DO NOTHING;"
            data = (aid, names[n])
            cur.execute(statement, data)
        statement = "SELECT w_wid FROM website WHERE w_wtitle = %s"
        cur.execute(statement, (web_name,))
        wid = cur.fetchone()
        # print(wid)
        # wid = wid[0]
        for e in range(len(es)):
            statement = "INSERT INTO episode(e_aid, e_wid, e_eurl, e_enum, e_edate) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (e_aid, e_wid, e_enum) DO NOTHING;"
            data = (aid, wid, es[e][0], es[e][1], es[e][2])
            cur.execute(statement, data)
    rds.commit()

def conn():
    # connect to S3
    s3 = boto3.client('s3', 'us-east-1', config=botocore.config.Config(region_name='us-east-1', s3={'addressing_style':'path'}))
    # ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
    # s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    print('Connect to S3 successfully')

    # connect to database
    DB_NAME = 'animedb'
    USER_NAME = 'animelover'
    USER_PWD = 'atpx4869'
    HOST_NAME = 'yucheninstancedb.cucvespz1pxc.us-east-1.rds.amazonaws.com'
    PORT_NUM = 5432
    rds = psycopg2.connect(database=DB_NAME, user=USER_NAME, password=USER_PWD, host=HOST_NAME, port=PORT_NUM)
    print('Connect to PostgreSQL successfully')

    return s3, rds

def load(s3, rds, web_name, date):
    start = datetime.datetime.now()

    bucketname = 'insightanimedata'
    key = web_name+'/'+date+'/anime_pages/'
    response = s3.list_objects_v2(Bucket=bucketname,Prefix=key)

    if 'Contents' in response:
        # recursion for getting all bojects
        while response['KeyCount'] == 1000:
              for item in response['Contents']:
                  if item['Key'] == key:
                      continue
                  print(item['Key'])
                  obj = s3.get_object(Bucket=bucketname, Key=item['Key'])
                  page= obj['Body'].read()
                #  print('inwhile')
                  loadtoDB(rds, web_name, page)
              response = s3.list_objects_v2(Bucket=bucketname, Prefix=key,StartAfter=item['Key'])
              print('----------- check key %s and count %d ----------------' % (item['Key'],  response['KeyCount']))
        for item in response['Contents']:
              if item['Key'] == key:
                  continue
              print(item['Key'])
              obj = s3.get_object(Bucket=bucketname, Key=item['Key'])
              page = obj['Body'].read()
           #   print('outwhile')
              loadtoDB(rds, web_name, page)
        end = datetime.datetime.now()
        print (start.strftime('Input into database starts at %Y-%m-%d %H:%M:%S'))
        print (end.strftime('Input into database ends at %Y-%m-%d %H:%M:%S'))
        print ('Process time = %s' % str(end - start))
    else:
        print('No such website or date')
    rds.close()

def userUpdateTrigger(timstamp):
    jsonData = {}
    jsonData['timestamp'] = timestamp
    msg=json.dumps(jsonData)
    client = boto3.client("sns")
    try:
        response = client.publish(TopicArn='arn:aws:sns:us-east-1:279380902069:UpdateTrigger', Message=msg)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Trigger userUpdate successfully.')

def lambda_handler(event, context):
    # msg = json.loads(event['Records'][0]['Sns']['Message'])
    # timestamp = msg['timestamp']
    timestamp = '2019-07-06'
    s3,rds = conn()

    t1 = threading.Thread(target=load, args=(s3, rds, '9anime', timestamp))
    t2 = threading.Thread(target=load, args=(s3, rds, 'crunchyroll', timestamp))
    t3 = threading.Thread(target=load, args=(s3, rds, 'kissanime', timestamp))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print('Multithreads finish!')

    # userUpdateTrigger(timestamp)
