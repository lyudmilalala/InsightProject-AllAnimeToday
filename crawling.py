from lxml.html import document_fromstring
import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

def crawling(driver, page_name, web_url):
    driver.get(web_url)
    # time.sleep(1)
    html = driver.page_source
    # with open('crawl_test/'+page_name+'.html', 'w') as f:
    #     f.write(html)
    return html

def crawl_9anime(type):
    if (type == 'init') or (type == 'update'):
        driver = webdriver.Chrome()
        ############# Determine the webpage to crawl ############
        url = ''
        a_pages = []
        e_pages = []
        if type == 'init':
            url = 'https://www1.9anime.nl/az-list'
        else:
            url = "https://www1.9anime.nl/ongoing"
        driver.get(url)
        ############# Count the total number of pages need to crawl ############
        page_count = driver.find_element_by_xpath('//*[@id="main"]/div/div[3]/div[2]/div[3]/form/span[3]').get_attribute('textContent')
        ############# Crawl pages of anime lists ############
        # for i in range(1, int(page_count)+1):
        for i in range(1, 5):
            page = crawling(driver, '9anime_list_page_'+str(i), url+'?page=' + str(i))
            a_pages.append(page)
            print('============ 9anime list page count %d ============' % i)
        ############# Crawl page of each anime in the lists ############
            tree = document_fromstring(page)
            a_names = tree.xpath('//*[@id="main"]/div/div[3]/div[2]/div[2]/div/div/a/text()')
            a_hrefs = tree.xpath('//*[@id="main"]/div/div[3]/div[2]/div[2]/div/div/a/@href')
            # assert len(a_hrefs)== 30,"ERROR: Number of anime on a page is not 30."
            for j in range(len(a_hrefs)):
            # for j in range(10):
                a_names[j] = "_".join(a_names[j].split())
                e_pages.append(crawling(driver, a_names[j], a_hrefs[j]))
                print('-------- anime on the page name: %s -------' % a_names[j])
        driver.close()
        if type == 'init':
            print('Initialize HTMLs of 9anime successfully.')
        else:
            url = "Update HTMLs of 9anime successfully."
        return a_pages, e_pages, a_names
    else:
        print('Type error for 9anime crawling')
        return False

def crawl_crunchyroll(type):
    if (type == 'init') or (type == 'update'):
        driver = webdriver.Chrome()
        ############# Determine the webpage to crawl ############
        url = ''
        a_pages = []
        e_pages = []
        # Initizalize
        if type == 'init':
            url = 'https://www.crunchyroll.com/videos/anime/alpha?group=all'
            ############# Crawl pages of anime lists ############
            page = crawling(driver, 'crunchyroll_list', url)
            a_pages.append(page)
            print('============ crunchyroll list page ============')
            ############# Crawl page of each anime in the lists ############
            tree = document_fromstring(page)
            a_names = tree.xpath('//*[@id="main_content"]/div[2]/div[1]/ul/li/a/text()')
            a_hrefs = tree.xpath('//*[@id="main_content"]/div[2]/div[1]/ul/li/a/@href')
            for j in range(len(a_names)):
            # for j in range(20):
                a_names[j] = '_'.join(a_names[j].strip().split())
                e_pages.append(crawling(driver, a_names[j], 'https://www.crunchyroll.com' + a_hrefs[j]))
                print('-------- anime on the page name: %s -------' % a_names[j])
            print('Initialize HTMLs of crunchyroll successfully.')
        # Update
        else:
            url = 'https://www.crunchyroll.com/videos/anime/updated'
            ############# Crawl pages of anime lists ############
            page = crawling(driver, 'crunchyroll_list', url)
            a_pages.append(page)
            print('============ crunchyroll ist page ============')
            ############# Crawl page of each anime in the lists ############
            tree = document_fromstring(page)
            a_names = tree.xpath('//*[@id="main_content"]/ul/li/div/a/@title')
            a_hrefs = tree.xpath('//*[@id="main_content"]/ul/li/div/a/@href')
            for j in range(len(a_names)):
            # for j in range(20):
                a_names[j] = '_'.join(a_names[j].strip().split())
                e_pages.append(crawling(driver, a_names[j], 'https://www.crunchyroll.com' + a_hrefs[j]))
                print('-------- anime on the page name: %s -------' % a_names[j])
            print('Update HTMLs of crunchyroll successfully.')
        driver.close()
        return a_pages, e_pages, a_names
    else:
        print('Type error for 9anime crawling')
        return False

def crawl_kissanime(type):
    if (type == 'init') or (type == 'update'):
        driver = webdriver.Chrome()
        ############# Determine the webpage to crawl ############
        url = ''
        a_pages = []
        e_pages = []
        page_count = 5
        if type == 'init':
            url = 'https://kissanime.ru/AnimeList'
        else:
            url = "https://kissanime.ru/AnimeList/LatestUpdate"
        driver.get(url)
        time.sleep(10)
        driver.get(url)
        if type == 'init':
            ############# Count the total number of pages need to crawl ############
            page_count = driver.find_element_by_xpath('//*[@id="leftside"]/div/div[3]/ul/li[5]/a').get_attribute('page')
        print(page_count)
        ############# Crawl pages of anime lists ############
        # for i in range(1, int(page_count)+1):
        for i in range(1, 5):
            page = crawling(driver, 'kissanime_list_page_'+str(i), url+'?page=' + str(i))
            a_pages.append(page)
            print('============ kissanime list page count %d ============' % i)
        ############# Crawl page of each anime in the lists ############
            tree = document_fromstring(page)
            a_names = tree.xpath('//*[@id="leftside"]/div/div[2]/div[4]/table/tbody/tr[@class="add"]/td[1]/a/text()')
            a_hrefs = tree.xpath('//*[@id="leftside"]/div/div[2]/div[4]/table/tbody/tr[@class="add"]/td[1]/a/@href')
            # assert len(a_hrefs) == 30,"ERROR: Number of anime on a page is not 30."
            # for i in range(len(a_hrefs)):
            for j in range(10):
                a_names[j] = '_'.join(a_names[j].strip().split())
                e_pages.append(crawling(driver, a_names[j], 'https://kissanime.ru' + a_hrefs[j]))
                print('-------- anime on the page name: %s -------' % a_names[j])
        driver.close()
        if type == 'init':
            print('Initialize HTMLs of Kissanime successfully.')
        else:
            url = "Update HTMLs of Kissanime successfully."
        return a_pages, e_pages, a_names
    else:
        print('Type error for Kissanime crawling')
        return False

def crawl_web(web_name, type):
    assert (type == 'init') or (type == 'update'), 'Type ERROR for Crawling: Please input "init" or "update"'
    if web_name == '9anime':
        return crawl_9anime(type)
    elif web_name == 'crunchyroll':
        return crawl_crunchyroll(type)
    elif web_name == 'kissanime':
        return crawl_kissanime(type)
    # add more website
    else:
        print('No such website')
        return -1

def extract():
    driver = webdriver.Chrome()
    url = 'https://kissanime.ru/AnimeList?page=1'
############# Crawl pages of anime lists ############
    page = crawling(driver, 'kissanime_list_page_1', url)
    print('============ kissanime list page ============')
############# Crawl page of each anime in the lists ############
    tree = document_fromstring(page)
    print(tree)
    a_names = tree.xpath('//*[@id="leftside"]/div/div[2]/div[4]/table[@class="listing"]/tbody/tr[2]/td[1]/a/text()')
    a_hrefs = tree.xpath('//*[@id="leftside"]/div/div[2]/div[4]/table[@class="listing"]/tbody/tr[2]/td[1]/a/@href')
    # assert len(a_hrefs) == 30,"ERROR: Number of anime on a page is not 30."
    # for i in range(len(a_hrefs)):
    # for j in range(len(a_names)):
    #     a_names[j] = '_'.join(a_names[j].strip().split())
    #     a_hrefs[j] = 'https://kissanime.ru' + a_hrefs[j]
    print(a_names)
    print(a_hrefs)
    # print(len(a_names))
    # print(len(a_hrefs))
    # driver.get(a_hrefs[3])
    driver.close()

# extract()
# crawl_web('kissanime', 'init')
