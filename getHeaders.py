from selenium import webdriver
from browsermobproxy import Server

from selenium.webdriver.chrome.options import Options
import time


# 获取accessToken
def getToken():
    server = Server(r'F:\browsermob-proxy-2.1.4\bin\browsermob-proxy.bat')
    server.start()
    proxy = server.create_proxy()

    chrome_options = Options()
    chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))

    driver = webdriver.Chrome(chrome_options=chrome_options)
    base_url = "http://jzsc.mohurd.gov.cn/data/company/detail?id=C5C5C4C3C5C2C7C7C5C5C0C2C7CCC7C7C5C6"
    proxy.new_har("douyin", options={'captureHeaders': True, 'captureContent': True})
    driver.get(base_url)
    while '验证已过期，是否重新重新进行验证或停留在当前页面？' in driver.page_source:
        driver.find_element_by_xpath('//*[@id="app"]/div/header/div[5]/div/div[3]/div/button[1]').click()
        time.sleep(2.5)
        driver.refresh()
        time.sleep(3)
    result = proxy.har
    token = set()
    for entry in result['log']['entries']:
        _url = entry['request']['url']
        if "api/webApi/dataservice/query/comp/caDetailList?qyId" in str(_url):
            _response = entry['request']
            _accessToken = entry['request']['headers'][4]['value']
            if _accessToken != '':
                token.add(_accessToken)
    server.stop()
    driver.quit()
    return list(token)[0]
