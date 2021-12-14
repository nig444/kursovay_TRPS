from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import json
from sqlharder import SQLharder
from selenium.webdriver.firefox.options import Options

var_geckodriver='./geckodriver'
db = SQLharder('kursovaya.db')
list_user=db.get_users_info()

options = Options()
options.headless = True

browser = webdriver.Firefox(options=options,executable_path = var_geckodriver)


while True:
    for user in list_user:

        browser.get(url="https://lks.bmstu.ru/portal3/login?back=https://lks.bmstu.ru/schedule/d2eb32ae-4aee-11e9-aa02-005056960017")
        username = browser.find_element_by_id("username")
        username.send_keys(user[1])
        password = browser.find_element_by_id("password")
        password.send_keys(user[2])
        password.send_keys(Keys.ENTER)
        sleep(2)
        site_for_get_data = browser.find_element_by_xpath("/html/body/div[2]/ul/li[2]/a").click()
        sleep(2)
        s = BeautifulSoup(browser.page_source, 'html.parser')
        l = s.find('table', {'class':'table table-striped table-bordered text-center table-responsive'})
        rs = l.findAll('tr')
        data=[]
        ii = 0
        for row in rs:
            elements=row.findAll('td')
            test = ""
            data.append([])
            for i in elements:
                data[ii].append(i.text)
                test+=i.text+" "
            print(test)
            ii+=1
        print('______________')
        browser.get(url="https://lks.bmstu.ru/portal3/logout?back=https://lks.bmstu.ru/progress")
        str = json.dumps(data)
        print(db.get_data(user[0]))
        if(str!=db.get_data(user[0])):
            db.update_data(user[0],str)
            print('update'+user[1])
        sleep(10)
    browser.close()
    browser.quit()
