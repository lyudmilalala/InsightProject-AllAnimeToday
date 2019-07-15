import json
import os
from selenium import webdriver

_id = input('Please enter the identifier (ka/9a/cr): ')
id_to_url = {
	'ka': 'https://kissanime.ru/AnimeList',
	'9a': 'https://www1.9anime.nl/az-list',
	'cr': 'https://www.crunchyroll.com/',
}
COOKIE_SAVE_PATH = '/Users/lyudmila/Desktop/insight/Project/cookie_tmp/cookies_{}.json'.format(_id)
HOST = 'ec2-user@ec2-54-163-47-73.compute-1.amazonaws.com'

driver = webdriver.Chrome()
driver.get(id_to_url[_id])
input('Press ENTER after you passed the security check: ')
cookies = driver.get_cookies()
with open(COOKIE_SAVE_PATH, 'w') as f:
	f.write(json.dumps(cookies))

os.system('scp -i /Users/lyudmila/.ssh/yuchen-IAM-keypair.pem {} {}:~/stest/'.format(COOKIE_SAVE_PATH, HOST))
