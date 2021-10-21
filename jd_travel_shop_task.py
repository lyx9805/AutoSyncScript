#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/21 6:05 下午
# @File    : jd_travel_shop_task.py
# @Project : scripts
# @Desc    : 热爱环游记下方店铺任务
import asyncio
import json
import aiohttp
from urllib.parse import urlencode, quote
from config import USER_AGENT
from utils.browser import open_browser, open_page, close_browser
from utils.jd_init import jd_init
from utils.console import println
from utils.logger import logger
from db.model import Code

@jd_init
class JdTravelShopTask:
    headers = {
        'referer': 'https://bunearth.m.jd.com/',
        'user-agent': USER_AGENT,
        'content-type': 'application/x-www-form-urlencoded'
    }

    async def request(self, session, function_id, body=None, method='POST'):
        """
        请求数据
        :param session:
        :param function_id:
        :param body:
        :param method:
        :return:
        """
        try:
            if not body:
                body = {}
            params = {
                'functionId': function_id,
                'body': json.dumps(body),
                'client': 'wh5',
                'clientVersion': '1.0.0',
            }
            url = 'https://api.m.jd.com/client.action?' + urlencode(params)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)

            text = await response.text()

            data = json.loads(text)
            if data.get('data', dict()) and data.get('code', 999) == 999:
                data['code'] = 999
            return data
        except Exception as e:
            return {'code': 999}

    async def get_shop_list(self, session):
        """
        获取店铺列表
        :param session:
        :return:
        """
        try:
            params = {
                'functionId': 'qryCompositeMaterials',
                'body': {
                    "qryParam": "[{\"type\":\"advertGroup\",\"mapTo\":\"babelCountDownFromAdv\",\"id\":\"05884370\"},"
                                "{\"type\":\"advertGroup\",\"mapTo\":\"feedBannerT\",\"id\":\"05860672\"},"
                                "{\"type\":\"advertGroup\",\"mapTo\":\"feedBannerS\",\"id\":\"05861001\"},"
                                "{\"type\":\"advertGroup\",\"mapTo\":\"feedBannerA\",\"id\":\"05861003\"},"
                                "{\"type\":\"advertGroup\",\"mapTo\":\"feedBannerB\",\"id\":\"05861004\"},"
                                "{\"type\":\"advertGroup\",\"mapTo\":\"feedBottomHeadPic\",\"id\":\"05872092\"},"
                                "{\"type\":\"advertGroup\",\"mapTo\":\"feedBottomData0\",\"id\":\"05908556\"},"
                                "{\"type\":\"advertGroup\",\"mapTo\":\"fissionData\",\"id\":\"05863777\"},"
                                "{\"type\":\"advertGroup\",\"mapTo\":\"newProds\",\"id\":\"05864483\"}]",
                    "activityId": "2vVU4E7JLH9gKYfLQ5EVW6eN2P7B", "pageId": "", "reqSrc": "", "applyKey": "jd_star"},
                'client': 'wh5',
                'clientVersion': '1.0.0',
                'uuid': 'a20a584859ecbfbe14d1c986aa3456a3b46c3b36'
            }
            url = 'https://api.m.jd.com/client.action?' + urlencode(params)
            response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            if data.get('code') != '0':
                return []
            item_list = data.get('data', dict()).get('feedBottomData0', dict()).get('list', list())
            shop_list = []

            for item in item_list:
                shop_list.append({
                    'shop_id': item['link'],
                    'vendor_id': item['extension']['shopInfo']['venderId']
                })

            return shop_list
        except Exception:
            return []

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            shop_list = await self.get_shop_list(session)
            for shop in shop_list:
                data = await self.request(session, 'jm_promotion_queryPromotionInfoByShopId', {"shopId":"59323","channel":20})
                println(data)
                break


if __name__ == '__main__':
    from config import JD_COOKIES
    app = JdTravelShopTask(**JD_COOKIES[0])
    asyncio.run(app.run())