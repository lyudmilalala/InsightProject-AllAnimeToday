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
    try:
        cur = conn.cursor()
        cur.execute('''DROP SCHEMA public CASCADE;''')
        cur.execute('''CREATE SCHEMA public;''')
        print('Database emptied successfully')

        cur.execute('''CREATE TABLE anime(
                         a_aid       SERIAL PRIMARY KEY,
                         a_aimg      varchar(2083)
                     );''')

        cur.execute('''CREATE TABLE a_names(
                        an_aid        integer,
                        an_atitle     varchar(255) NOT NULL,
                        FOREIGN KEY (an_aid) REFERENCES anime(a_aid),
                        UNIQUE (an_atitle)
                     );''')

        cur.execute('''CREATE INDEX a_by_name ON a_names(an_atitle);''')

        cur.execute('''CREATE TABLE website(
                         w_wid       SERIAL PRIMARY KEY,
                         w_wtitle    varchar(255) NOT NULL
                     );''')

        cur.execute('''CREATE INDEX w_by_name ON website(w_wtitle);''')

        cur.execute('''CREATE TABLE episode(
                         e_eid       SERIAL PRIMARY KEY,
                         e_aid       integer NOT NULL,
                         e_wid       integer NOT NULL,
                         e_eurl      varchar(2083),
                         e_enum      varchar(255) NOT NULL,
                         e_edate     date,
                         FOREIGN KEY (e_aid) REFERENCES anime(a_aid),
                         FOREIGN KEY (e_wid) REFERENCES website(w_wid),
                         UNIQUE (e_aid, e_wid, e_enum)
                     );''')

        cur.execute('''CREATE INDEX e_by_dates ON episode(e_edate);''')

        cur.execute('''CREATE TABLE userinfo(
                         u_username      varchar(20),
                         u_psw           varchar(20) NOT NULL,
                         u_useremail     varchar(128) NOT NULL,
                         PRIMARY KEY (u_username)
                     );''')

        cur.execute('''CREATE TABLE following(
                        f_username   varchar(20),
                        f_aid        integer,
                        FOREIGN KEY (f_username) REFERENCES userinfo(u_username),
                        FOREIGN KEY (f_aid) REFERENCES anime(a_aid),
                        UNIQUE (f_username, f_aid)
                     );''')

        cur.execute('''INSERT INTO website(w_wtitle) VALUES ('9anime'), ('crunchyroll'), ('kissanime');''')

        cur.execute('''CREATE TABLE common_path(
                 cp_cpid           SERIAL PRIMARY KEY,
                 cp_level        integer NOT NULL,
                 cp_type         varchar(128) NOT NULL
             );''')

        cur.execute('''CREATE TABLE tags(
                 t_cpid           integer,
                 t_tag            varchar(128),
                 t_value          varchar(128),
                 FOREIGN KEY (t_cpid) REFERENCES common_path(cp_cpid)
             );''')

        cur.execute('''INSERT INTO common_path(cp_level, cp_type) VALUES
             (1, 'div'),
             (2, 'div'),
             (3, 'div'),
             (3, 'ul'),
             (4, 'li');''')

        cur.execute('''INSERT INTO tags(t_cpid, t_tag, t_value) VALUES
             (1, 'id', 'main'),
             (2, 'id', 'container'),
             (3, 'id', 'episode_list'),
             (4, 'class', 'list-of-seasons'),
             (3, 'class', 'content_wrapper');''')

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
        wlist = ['9anime', 'crunchyroll', 'kissanime']
        for w in wlist:
            a_pages, e_pages, a_names = crawling.crawl_web(w, 'init')
        print('Initial HTMLs are successfully crawled and stored into S3')
        return True
    except NoCredentialsError:
        print('Credentials not available')
    return False


# initS3()
initPostgres()
# initData()
