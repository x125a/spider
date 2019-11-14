from aiohttp import ClientSession
import aiohttp, asyncio
from spider.util.getHeaders import getToken
from spider.util.decrypt import decrypts
from spider.db.Mysql_db import MySQLClient
from spider.db.Redis_db import RedisClient

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'jzsc.mohurd.gov.cn',
    'Upgrade-Insecure-Requests': '1',
    'accessToken': 'jkFXxgu9TcpocIyCKmJ+tfpxe/45B9dbWMUXhdY7vLUWsI9GvHTvT1LQxf8jSfGZhpUUKvcMtoMqfGfwdLCb8g=='
}


class SpiderMain(object):

    def __init__(self):
        self._redis = RedisClient()
        self._mysql = MySQLClient()
        self._HEADERS = HEADERS

    async def get_one_page(self, url):
        try:
            async with ClientSession() as session:
                async with session.get(url, headers=self._HEADERS) as r:
                    # res = decrypts(r.text)
                    return await r.text()
        except Exception as e:
            print('请求异常： ' + str(e))
            return {}

    # 并发爬取
    async def main(self, urls):
        # 任务列表
        tasks = [self.get_one_page(url) for url in urls]
        # 并发执行并保存每一个任务的返回结果
        results = await asyncio.gather(*tasks)
        # 返回解析为字典的数据
        if '4bd02be856577e3e61e83b86f51afca55280b5ee9ca16beb9b2a65406045c9497c089d5e8ff97c63000f62b011a6' \
           '4f4019b64d9a050272bd5914634d030aab69' in results:
            accessToken = getToken()
            self._HEADERS = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accessToken': accessToken}
            print(accessToken)
            await self.main(urls)
        # 保存数据
        self.__saveJsonData__(data=results)
        # for i in results:
        #     print(decrypts(i))

    def __getMaxPage__(self):
        pass

    def __getID__(self, rediskey=None):
        return self._redis.batch(rediskey=rediskey)

    def __findOneID__(self, idx=None, rediskey=None):
        return self._redis.exists(idx=idx, rediskey=rediskey)

    def __saveOneID__(self, idx=None, rediskey=None, score=None):
        if score is not None:
            self._redis.add(idx=idx, rediskey=rediskey, score=score)
        else:
            self._redis.add(idx=idx, rediskey=rediskey)

    def __saveone__(self, idx=None, rediskey=None):
        self._redis.add_one(idx=idx, rediskey=rediskey)

    def __deleteID__(self, idx=None, rediskey=None):
        return self._redis.deletes(idx=idx, rediskey=rediskey)

    def __saveListID__(self, list_id, rediskey=None):
        for idx in list_id:
            self._redis.add(idx=idx, rediskey=rediskey)

    def __saveOneData__(self, table_name, data):
        print(data)
        return self._mysql.__insertData__(table_name=table_name, data=data)

    def __closeMysql__(self):
        try:
            self._mysql.__closeDB__()
        except Exception as e:
            print('Close Mysql failed!', e)

    def run(self, data_list):
        datas = [data_list[x:x + 5] for x in range(0, len(data_list), 5)]
        for data in datas:
            self.__spiderInfo__(data=data)


