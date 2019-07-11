from flask import Flask,render_template,url_for,redirect
from flask import request
import psycopg2
import json
import math

#create Flask instqnce
app=Flask(__name__)

# connect to database
def conn():
    DB_NAME = 'animedb'
    USER_NAME = 'animelover'
    USER_PWD = 'atpx4869'
    HOST_NAME = 'yucheninstancedb.cucvespz1pxc.us-east-1.rds.amazonaws.com'
    PORT_NUM = 5432
    rds = psycopg2.connect(database=DB_NAME, user=USER_NAME, password=USER_PWD, host=HOST_NAME, port=PORT_NUM)
    print('Connect to PostgreSQL successfully')
    return rds

@app.route("/", methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/here', methods=['GET', 'POST'])
def display():
    # import pdb;pdb.set_trace()
    name = request.args['name']
    return render_template('main.html', name=name)

@app.route("/signin", methods=['GET', 'POST'])
def signin():
    rds = conn()
    name = request.form['Name']
    psw = request.form['Psw']
    try:
        cur = rds.cursor()
        statement = "SELECT u_username FROM userinfo WHERE u_username = %s AND u_psw = %s;"
        cur.execute(statement, (name,psw))
        rows = cur.fetchall()
        if len(rows) == 0:
            s = 0
        else:
            s = 1
    except psycopg2.DatabaseError as error:
        print(error)
        s = -1
    finally:
        cur.close()
        rds.close()
        j = json.dumps({'status': s})
    return j

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    rds = conn()
    name = request.form['Name']
    email = request.form['Email']
    psw = request.form['Psw']
    s = -1
    try:
        cur = rds.cursor()
        statement = "SELECT u_username FROM userinfo WHERE u_username = %s;"
        cur.execute(statement, (name,))
        rows = cur.fetchall()
        if len(rows) == 0:
            cur.execute("INSERT INTO userinfo VALUES (%s, %s, %s);", (name, psw, email))
            rds.commit()
            s = 1
        else:
            s = 0
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        cur.close()
        rds.close()
        j = json.dumps({'status': s})
    return j

@app.route("/getPage", methods=['GET', 'POST'])
def getPage():
    rds = conn()
    # import pdb; pdb.set_trace()
    count = request.form['Count']
    name = request.form['Name']
    print(count)
    jsonData = {}
    try:
        cur = rds.cursor()
        cur.execute("SELECT COUNT(a_aid) FROM anime;")
        total = math.ceil(int(cur.fetchone()[0])/35)
        jsonData['total'] = total
        start = (int(count)-1)*35
        statement = "SELECT an_atitle, a_aimg FROM a_names, anime WHERE an_atitle = (SELECT an_atitle FROM a_names WHERE a_aid = an_aid LIMIT 1) LIMIT 35 OFFSET %s;"
        cur.execute(statement, (start,))
        result = cur.fetchall()
        titles = []
        imgs = []
        for r in result:
            titles.append(r[0])
            imgs.append(r[1])
        jsonData['titles'] = titles
        jsonData['imgs'] = imgs
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        cur.close()
        rds.close()
        j=json.dumps(jsonData)
        # print(j)
    return j

@app.route("/search", methods=['GET', 'POST'])
def search():
    rds = conn()
    title = request.form['Title']
    title = title.title()
    print(title)
    jsonData = {}
    try:
        cur = rds.cursor()
        statement = "SELECT an_aid FROM a_names WHERE an_atitle LIKE '%"+title+"%' GROUP BY an_aid;"
        cur.execute(statement)
        result = cur.fetchall()
        titles = []
        imgs = []
        for r in range(len(result)):
            id = result[r][0]
            statement = "SELECT an_atitle, a_aimg FROM a_names, anime WHERE an_atitle = (SELECT an_atitle FROM a_names WHERE a_aid = an_aid LIMIT 1) AND a_aid = "+ str(id) +";"
            cur.execute(statement)
            temp = cur.fetchone()
            titles.append(temp[0])
            imgs.append(temp[1])
        jsonData['titles'] = titles
        jsonData['imgs'] = imgs
    except psycopg2.DatabaseError as error:
        print(error)
        return -1
    finally:
        cur.close()
        rds.close()
        j=json.dumps(jsonData)
    return j

@app.route('/info', methods=['GET', 'POST'])
def info():
    rds = conn()
    title = request.args['title']
    user = request.args['user']
    status = ''
    jsonData = {}
    try:
        cur = rds.cursor()
        statement = "SELECT FROM following WHERE f_username = %s AND f_aid = (SELECT an_aid FROM a_names WHERE an_atitle = %s);"
        cur.execute(statement,(user, title))
        if len(cur.fetchall()) > 0:
            status = 'unsubscribe'
        else:
            status = 'subscribe'
        statement = "SELECT e_enum, e_eurl FROM episode, a_names WHERE an_atitle = '"+title+"' AND an_aid = e_aid;"
        cur.execute(statement)
        result = cur.fetchall()
        for r in range(len(result)):
            num = result[r][0]
            url = result[r][1]
            if num in jsonData:
                jsonData[num].append(url)
            else:
                jsonData[num] = []
                jsonData[num].append(url)
    except psycopg2.DatabaseError as error:
        print(error)
        return -1
    finally:
        cur.close()
        rds.close()
        j=json.dumps(jsonData)
    return render_template('info.html', title=title, user = user, status = status, data = j)

@app.route("/subscribe", methods=['GET', 'POST'])
def click():
    print('in sub')
    va = request.form['Status']
    uname = request.form['User']
    aname = request.form['Title']
    rds = conn()
    s = -1
    try:
        cur = rds.cursor()
        if va == 'subscribe':
            statement = "INSERT INTO following (f_username, f_aid) SELECT %s, an_aid FROM a_names WHERE an_atitle = %s;"
            # print(statement % (uname, aname))
            cur.execute(statement,(uname, aname))
        else:
            statement = "DELETE FROM following WHERE f_username = %s AND f_aid = (SELECT an_aid FROM a_names WHERE an_atitle = %s);"
            # print(statement % (uname, aname))
            cur.execute(statement,(uname, aname))
        rds.commit()
        s = 1
    except psycopg2.DatabaseError as error:
        print(error)
        s = -1
    finally:
        cur.close()
        rds.close()
        j = json.dumps({'status': s})
    return j

if __name__ == '__main__':
    app.run()
