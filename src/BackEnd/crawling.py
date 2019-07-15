from lxml.html import document_fromstring
import time
import datetime
from selenium import webdriver
import boto3
from botocore.exceptions import NoCredentialsError

def getKey():
    with open('../myKeys.txt', 'r') as f:
        line = f.readline()
        map = line.strip().split(',')
    return map[0], map[1], map[2]

def crawling(driver, page_name, web_url):
    driver.get(web_url)
    time.sleep(1)
    html = driver.page_source
    with open('../crawl_test/kissanime/'+page_name+'.html', 'w') as f:
        f.write(html)
    return html

def crawl_9anime(type, s3):
    start = datetime.datetime.now()

    if (type == 'init') or (type == 'update'):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-gpu")
        options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        driver = webdriver.Chrome(executable_path= './chromedriver', chrome_options=options)
        driver.get('https://google.com')
        with open('cookies_9a.json', 'r') as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                 driver.add_cookie(cookie)
        ############# Determine the webpage to crawl ############
        url = ''
        a_pages = []
        e_pages = []
        a_names = []
        if type == 'init':
            url = 'https://www1.9anime.nl/az-list'
            key = 'init'
        else:
            url = "https://www1.9anime.nl/updated"
            key = datetime.datetime.now().strftime('%Y-%m-%d')

        ############## Build the s3 directories ##############
        bucketname = 'insightanimedata'
        s3.put_object(Bucket=bucketname, Key='9anime/'+key+'/')
        s3.put_object(Bucket=bucketname, Key='9anime/'+key+'/list_pages/')
        s3.put_object(Bucket=bucketname, Key='9anime/'+key+'/anime_pages/')

        driver.get(url)
        ############# Count the total number of pages need to crawl ############
        page_count = driver.find_element_by_xpath('//*[@id="main"]/div/div[3]/div[2]/div[3]/form/span[3]').get_attribute('textContent')
        if type == 'init':
            end = int(page_count)+1
        else:
            end = 10
        ############# Crawl pages of anime lists ############
        for i in range(1, end):
        # 50-150
        # for i in range(1, 2):
            page = crawling(driver, '9anime_list_page_'+str(i), url+'?page=' + str(i))
            a_pages.append(page)
            s3.put_object(Bucket=bucketname, Key='9anime/'+key+'/list_pages/'+str(i+1)+'.html', Body=page)
            print('============ 9anime list page count %d ============' % i)
        ############# Crawl page of each anime in the lists ############
            tree = document_fromstring(page)
            if type == 'init':
                temp_names = tree.xpath('//div[@id="main"]/div/div[3]/div[2]/div[2]/div[@class="item"]/div[@class="info"]/a[@class="name"]/text()')
                temp_hrefs = tree.xpath('//div[@id="main"]/div/div[3]/div[2]/div[2]//div[@class="item"]/div[@class="info"]/a[@class="name"]/@href')
            else:
                temp_names = tree.xpath('//div[@id="main"]/div/div[3]/div[2]/div[2]/div[@class="item"]/div[@class="inner"]/a[@class="name"]/text()')
                temp_hrefs = tree.xpath('//div[@id="main"]/div/div[3]/div[2]/div[2]/div[@class="item"]/div[@class="inner"]/a[@class="name"]/@href')
            # assert len(a_hrefs)== 30,"ERROR: Number of anime on a page is not 30."
            for j in range(len(temp_hrefs)):
            # for j in range(10):
                temp_names[j] = "_".join(temp_names[j].split())
                temp_names[j] = temp_names[j].replace('//', '_')
                temp_names[j] = temp_names[j].replace('/', '_')
                a_names.append(temp_names[j])
                ep = crawling(driver, temp_names[j], temp_hrefs[j])
                e_pages.append(ep)
                s3.put_object(Bucket=bucketname, Key='9anime/'+key+'/anime_pages/'+temp_names[j]+'.html', Body=ep)
                print('-------- anime on the page name: %s -------' % temp_names[j])
        driver.close()
        if type == 'init':
            print('Initialize HTMLs of 9anime successfully.')
        else:
            url = "Update HTMLs of 9anime successfully."
        end = datetime.datetime.now()
        print (start.strftime('Crawling 9anime starts at %Y-%m-%d %H:%M:%S'))
        print (end.strftime('Crawling 9anime ends at %Y-%m-%d %H:%M:%S'))
        print ('Process time = %s' % str(end - start))
        # print('a_pages size %d, a_names size %d, e_pages size %d' % (len(a_pages), len(a_names), len(e_pages)))
        return a_pages, e_pages, a_names
    else:
        print('Type error for 9anime crawling')
        return False

def crawl_crunchyroll(type, s3):
    start = datetime.datetime.now()

    if (type == 'init') or (type == 'update'):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-gpu")
        options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        driver = webdriver.Chrome(executable_path= './chromedriver', chrome_options=options)
        driver.get('https://google.com')
        with open('cookies_cr.json', 'r') as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                 driver.add_cookie(cookie)
        ############# Determine the webpage to crawl ############
        url = ''
        a_pages = []
        e_pages = []
        a_names = []
        # Initizalize
        if type == 'init':
            url = 'https://www.crunchyroll.com/videos/anime/alpha?group=all'
            key = 'init'
        else:
            url = 'https://www.crunchyroll.com/videos/anime/updated'
            key = datetime.datetime.now().strftime('%Y-%m-%d')

        ############## Build the s3 directories ##############
        bucketname = 'insightanimedata'
        s3.put_object(Bucket=bucketname, Key='crunchyroll/'+key+'/')
        s3.put_object(Bucket=bucketname, Key='crunchyroll/'+key+'/list_pages/')
        s3.put_object(Bucket=bucketname, Key='crunchyroll/'+key+'/anime_pages/')

        ############# Crawl pages of anime lists ############
        page = crawling(driver, 'crunchyroll_list', url)
        a_pages.append(page)
        s3.put_object(Bucket=bucketname, Key='crunchyroll/'+key+'/list_pages/1.html', Body=page)
        print('============ crunchyroll list page ============')
        ############# Crawl page of each anime in the lists ############
        tree = document_fromstring(page)
        if type == 'init':
            temp_names = tree.xpath('//*[@id="main_content"]/div[2]/div[@class="videos-column left"]/ul/li/a/text()')
            temp_hrefs = tree.xpath('//*[@id="main_content"]/div[2]/div[@class="videos-column left"]/ul/li/a/@href')
        else:
            temp_names = tree.xpath('//*[@id="main_content"]/ul/li/div/a/@title')
            temp_hrefs = tree.xpath('//*[@id="main_content"]/ul/li/div/a/@href')
        for j in range(len(temp_names)):
            temp_names[j] = '_'.join(temp_names[j].strip().split())
            temp_names[j] = temp_names[j].replace('//', '_')
            temp_names[j] = temp_names[j].replace('/', '_')
            a_names.append(temp_names[j])
            ep = crawling(driver, temp_names[j], 'https://www.crunchyroll.com' + temp_hrefs[j])
            e_pages.append(ep)
            s3.put_object(Bucket=bucketname, Key='crunchyroll/'+key+'/anime_pages/'+temp_names[j]+'.html', Body=ep)
            print('-------- anime on the page name: %s -------' % a_names[j])
        if type == 'init':
            print('Initialize HTMLs of crunchyroll successfully.')
        else:
            print('Update HTMLs of crunchyroll successfully.')
        driver.close()
        end = datetime.datetime.now()
        print (start.strftime('Crawling crunchyroll starts at %Y-%m-%d %H:%M:%S'))
        print (end.strftime('Crawling crunchyroll ends at %Y-%m-%d %H:%M:%S'))
        print ('Process time = %s' % str(end - start))
        return a_pages, e_pages, a_names
    else:
        print('Type error for 9anime crawling')
        return False

def crawl_kissanime(type, s3):
    start = datetime.datetime.now()

    if (type == 'init') or (type == 'update'):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-gpu")
        options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        driver = webdriver.Chrome(executable_path= './chromedriver', chrome_options=options)
        driver.get('https://google.com')
        with open('cookies_ka.json', 'r') as f:
            cookies = json.loads(f.read())
            for cookie in cookies:
                driver.add_cookie(cookie)
        ############# Determine the webpage to crawl ############
        url = ''
        a_pages = []
        e_pages = []
        a_names = []
        if type == 'init':
            url = 'https://kissanime.ru/AnimeList'
            key = 'init'
        else:
            url = "https://kissanime.ru/AnimeList/LatestUpdate"
            key = datetime.datetime.now().strftime('%Y-%m-%d')

        ############## Build the s3 directories ##############
        bucketname = 'insightanimedata'
        s3.put_object(Bucket=bucketname, Key='kissanime/'+key+'/')
        s3.put_object(Bucket=bucketname, Key='kissanime/'+key+'/list_pages/')
        s3.put_object(Bucket=bucketname, Key='kissanime/'+key+'/anime_pages/')

        driver.get(url)
        time.sleep(7)
        driver.get(url)
        ############# Count the total number of pages need to crawl ############
        page_count = driver.find_element_by_xpath('//*[@id="leftside"]/div/div[3]/ul/li[5]/a').get_attribute('page')
        if type == 'init':
            end = int(page_count)+1
        else:
            end = 7
        # print(page_count)
        ############# Crawl pages of anime lists ############
        for i in range(1, end):
        # for i in range(80, 130):
            page = crawling(driver, 'kissanime_list_page_'+str(i), url+'?page=' + str(i))
            a_pages.append(page)
            s3.put_object(Bucket=bucketname, Key='kissanime/'+key+'/list_pages/'+str(i+1)+'.html', Body=page)
            print('============ kissanime list page count %d ============' % i)
        ############# Crawl page of each anime in the lists ############
            tree = document_fromstring(page)
            temp_names = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[@class="bigBarContainer"]/div[@class="barContent"]/div/table[@class="listing"]/tbody/tr/td[1]/a/text()')
            temp_hrefs = tree.xpath('//div[@id="containerRoot"]/div[@id="container"]/div[@id="leftside"]/div[@class="bigBarContainer"]/div[@class="barContent"]/div/table[@class="listing"]/tbody/tr/td[1]/a/@href')
            # assert len(a_hrefs) == 30,"ERROR: Number of anime on a page is not 30."
            for j in range(len(temp_hrefs)):
            # for j in range(10):
                temp_names[j] = "_".join(temp_names[j].split())
                temp_names[j] = temp_names[j].replace('//', '_')
                temp_names[j] = temp_names[j].replace('/', '_')
                a_names.append(temp_names[j])
                ep = crawling(driver, temp_names[j], 'https://kissanime.ru' + temp_hrefs[j])
                e_pages.append(ep)
                s3.put_object(Bucket=bucketname, Key='kissanime/'+key+'/anime_pages/'+temp_names[j]+'.html', Body=ep)
                print('-------- anime on the page name: %s -------' % temp_names[j])
        driver.close()
        if type == 'init':
            print('Initialize HTMLs of Kissanime successfully.')
        else:
            url = "Update HTMLs of Kissanime successfully."
        end = datetime.datetime.now()
        print (start.strftime('Crawling Kissanime starts at %Y-%m-%d %H:%M:%S'))
        print (end.strftime('Crawling Kissanime ends at %Y-%m-%d %H:%M:%S'))
        print ('Process time = %s' % str(end - start))
        return a_pages, e_pages, a_names
    else:
        print('Type error for Kissanime crawling')
        return False

def crawl_web(web_name, type):
    assert (type == 'init') or (type == 'update'), 'Type ERROR for Crawling: Please input "init" or "update"'
    ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
    s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    print('Connect to S3 successfully')
    if web_name == '9anime':
        crawl_9anime(type, s3)
    elif web_name == 'crunchyroll':
        crawl_crunchyroll(type, s3)
    elif web_name == 'kissanime':
        crawl_kissanime(type, s3)
    # add more website
    else:
        print('No such website')
        return -1

def main():
    t1 = threading.Thread(target=crawl_web, args=('9anime', 'update'))
    t2 = threading.Thread(target=crawl_web, args=('crunchyroll', 'update'))
    t3 = threading.Thread(target=crawl_web, args=('kissanime', 'update'))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    ACCESS_KEY, SECRET_KEY, ACCOUNT_REGION = getKey()
    sns = boto3.client('sns',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    jsonData = {}
    jsonData['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d')
    msg=json.dumps(jsonData)
    try:
        response = client.publish(TopicArn='arn:aws:sns:us-east-1:279380902069:ExtractTrigger', Message=msg)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Trigger userUpdate successfully.')
# def extract():
#     driver = webdriver.Chrome()
#     url = 'https://www.crunchyroll.com/videos/anime/alpha?group=all'
#     ############# Crawl pages of anime lists ############
#     page = crawling(driver, 'crunchyroll_list', url)
#     # a_pages.append(page)
#     # print('============ crunchyroll list page ============')
#     ############# Crawl page of each anime in the lists ############
#     tree = document_fromstring(page)
#     a_names = tree.xpath('//*[@id="main_content"]/div[2]/div[@class="videos-column left"]/ul/li/a/text()')
#     print(a_names)
#     driver.close()

# extract()
# crawl_web('kissanime', 'init')
# crawl_crunchyroll('init')
