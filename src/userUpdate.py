import psycopg2
import datetime
import boto3
from botocore.exceptions import ClientError

def conn():
    DB_NAME = 'animedb'
    USER_NAME = 'animelover'
    USER_PWD = 'atpx4869'
    HOST_NAME = 'yucheninstancedb.cucvespz1pxc.us-east-1.rds.amazonaws.com'
    PORT_NUM = 5432
    rds = psycopg2.connect(database=DB_NAME, user=USER_NAME, password=USER_PWD, host=HOST_NAME, port=PORT_NUM)
    print('Connect to PostgreSQL successfully')
    return rds

def checkIndividualUpdate (username, useremail, usertext, date):
    rds = conn()
    cur = rds.cursor()
    # date = datetime.datetime.now().strftime('%Y-%m-%d')
    statement = "SELECT an_atitle, e_enum, e_eurl FROM a_names, episode, following WHERE e_edate = '"+date+"' AND f_username = '"+username+"' AND an_atitle = (SELECT an_atitle FROM a_names WHERE an_aid = e_aid AND f_aid=an_aid LIMIT 1);"
    cur.execute(statement)
    rows = cur.fetchall()
    if len(rows) > 0:
        content = {}
        for r in rows:
            title = r[0]
            enum = r[1]
            eurl = r[2]
            if title in content:
                episodes = content[title]
                if enum in episodes:
                    episodes[enum].append(eurl)
                else:
                    episodes[enum] = []
                    episodes[enum].append(eurl)
            else:
                content[title] = {}
                content[title][enum] = []
                content[title][enum].append(eurl)
        jsonData = {}
        jsonData['type'] = 'user'
        jsonData['username'] = username
        jsonData['email'] = useremail
        jsonData['number'] = usertext
        jsonData['payload'] = content
        msg=json.dumps(jsonData)
        client = boto3.client("sns")
        try:
            response = client.publish(TopicArn='arn:aws:sns:us-east-1:279380902069:MessageTrigger', Message=msg)
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print('Trigger messageSender successfully.')
    rds.close()

def checkUpdate(date):
    rds = conn()
    cur = rds.cursor()
    statement = "SELECT DISTINCT f_username, u_useremail, u_usertext FROM userinfo,following WHERE f_username=u_username;"
    cur.execute(statement)
    rows = cur.fetchall()
    print(rows)
    for r in rows:
        checkIndividualUpdate(r[0], r[1], r[2], date)
    rds.close()

def lambda_handler(event, context):
    msg = json.loads(event['Records'][0]['Sns']['Message'])
    timestamp = msg['timestamp']
    checkUpdate(timestamp)
