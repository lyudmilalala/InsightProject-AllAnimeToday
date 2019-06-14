# -*- coding:UTF-8 -*-
import psycopg2
import boto3
import crawling
from botocore.exceptions import NoCredentialsError

def getKey():
    with open('myKeys.txt', 'r') as f:
        line = f.readline()
        map = line.strip().split(',')
    return map[0], map[1], map[2]

def initPostgres():
    DB_NAME = 'animedb'
    USER_NAME = 'animelover'
    USER_PWD = 'atpx4869'
    HOST_NAME = 'yucheninstancedb.cucvespz1pxc.us-east-1.rds.amazonaws.com'
    PORT_NUM = 5432
    conn = psycopg2.connect(database=DB_NAME, user=USER_NAME, password=USER_PWD, host=HOST_NAME, port=PORT_NUM)
    print('connect to PostgreSQL success')
    cur = conn.cursor()
    try:
        cur = conn.cursor()
        cur.execute('''DROP SCHEMA public CASCADE;''')
        cur.execute('''CREATE SCHEMA public;''')
        cur.execute('''CREATE TABLE anime(
                         a_aid       integer,
                         a_atitle    varchar(255) NOT NULL,
                         a_aimg      varchar(2083),
                         a_language  varchar(255),
                         PRIMARY KEY (a_aid)
                     );''')

        cur.execute('''CREATE TABLE website(
                         w_wid       integer,
                         w_wtitle    varchar(255) NOT NULL,
                         PRIMARY KEY (w_wid)
                     );''')

        cur.execute('''CREATE TABLE ani_web(
                         aw_aid      integer,
                         aw_wid      integer,
                         aw_aurl     varchar(255) NOT NULL,
                         aw_adate     date,
                         PRIMARY KEY (aw_aurl),
                         FOREIGN KEY (aw_aid) REFERENCES anime(a_aid),
                         FOREIGN KEY (aw_wid) REFERENCES website(w_wid),
                         UNIQUE (aw_aid, aw_wid)
                     );''')

        cur.execute('''CREATE TABLE epi_web(
                         e_eurl      varchar(2083),
                         e_aurl      varchar(2083),
                         e_enum      integer NOT NULL,
                         e_edate     date,
                         PRIMARY KEY (e_eurl),
                         FOREIGN KEY (e_aurl) REFERENCES ani_web(aw_aurl)
                     );''')

        cur.execute('''CREATE INDEX by_dates ON epi_web(e_edate);''')

        cur.execute('''CREATE TABLE userinfo(
                         u_username      varchar(20),
                         u_useremail     varchar(128),
                         PRIMARY KEY (u_username)
                     );''')

        cur.execute('''CREATE TABLE following(
                        f_username   varchar(20),
                        f_aid        integer,
                        FOREIGN KEY (f_username) REFERENCES userinfo(u_username),
                        FOREIGN KEY (f_aid) REFERENCES anime(a_aid),
                        UNIQUE (f_username, f_aid)
                     );''')

        conn.commit()
        print("Tables created successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return False
    finally:
        if cur:
            cur.close()
    conn.close()
    return True

def initS3():
    ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
    bucketname = 'insightanimedata'
    s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    try:
        # empty the bucket
        response = s3.list_objects_v2(Bucket=bucketname)
        if 'Contents' in response:
            for item in response['Contents']:
                print('deleting file', item['Key'])
                s3.delete_object(Bucket=bucketname, Key=item['Key'])
                while response['KeyCount'] == 1000:
                    response = s3.list_objects_v2(
                        Bucket=bucketname,
                        StartAfter=response['Contents'][0]['Key']
                    )
                    for item in response['Contents']:
                        print('deleting file', item['Key'])
                        s3.delete_object(Bucket=bucketname, Key=item['Key'])
        print('Bucket emptied successfully')
        return True
    except NoCredentialsError:
        print('Credentials not available')
        return False

def initData():
    ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
    bucketname = 'insightanimedata'
    s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    try:
        wlist = ['crunchyroll']
        for w in wlist:
            s3.put_object(Bucket=bucketname, Key=w+'/')
            s3.put_object(Bucket=bucketname, Key=w+'/init/')
            s3.put_object(Bucket=bucketname, Key=w+'/init/list_pages/')
            s3.put_object(Bucket=bucketname, Key=w+'/init/anime_pages/')
            a_pages, e_pages, a_names = crawling.crawl_web(w, 'init')
            for i in range(len(a_pages)):
                s3.put_object(Bucket=bucketname, Key=w+'/init/list_pages/'+str(i+1)+'.html', Body=a_pages[i])
            for i in range(len(e_pages)):
                s3.put_object(Bucket=bucketname, Key=w+'/init/anime_pages/'+a_names[i]+'.html', Body=e_pages[i])
        print('Initial HTMLs are successfully crawled and stored into S3')
        return True
    except NoCredentialsError:
        print('Credentials not available')
    return False


initS3()
initPostgres()
initData()
