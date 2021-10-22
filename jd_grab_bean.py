#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/10/22 2:40 下午
# @File    : jd_grab_bean.py
# @Project : scripts
# @Desc    : 限时抢京豆
import asyncio
import aiohttp
import json
from urllib.parse import urlencode
from config import USER_AGENT
from utils.console import println
from utils.jd_init import jd_init
from db.model import Code


CODE_KEY = 'jd_grab_bean'


@jd_init
class JdGrabBean:

    headers = {
        'referer': 'https://bunearth.m.jd.com/',
        'user-agent': USER_AGENT,
        'content-type': 'application/x-www-form-urlencoded'
    }

    async def request(self, session, function_id, body=None, method='GET'):
        """
        :param method:
        :param body:
        :param function_id:
        :param session:
        :return:
        """
        try:
            if not body:
                body = {}

            params = {
                'functionId': function_id,
                'body': json.dumps(body),
                'clientVersion': '1.0.0',
                'appid': 'smtTimeLimitFission',
                'jsonp': ''
            }

            url = 'https://api.m.jd.com/client.action?' + urlencode(params)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)

            text = await response.text()

            data = json.loads(text)

            return data.get('result', dict())

        except Exception as e:
            println('{}, 请求服务器数据错误, {}'.format(self.account, e.args))
            return dict()

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:

            data = await self.request(session, 'smt_newFission_index')
            if not data:
                println('{}, 获取首页数据失败, 退出程序!'.format(self.account))
            project_id = data.get('projectId', '')
            task_list = data.get('taskInfoList', list())

            for task in task_list:
                if task.get('completionFlag', False):
                    continue
                assignment_id = task.get('assignmentId', '')
                task_type = task.get('type', '1')

                if task_type == '1':
                    res = await self.request(session, 'smt_newFission_doAssignment', {
                        "projectId": project_id, "assignmentId": assignment_id, "type": task.get('type', task_type),
                    })
                    println(res)
                elif task_type in ['3', '5', '6']:
                    item_list = task.get('ext')
                    for item in item_list:
                        params = {
                            "projectId": project_id, "assignmentId": assignment_id, "type": task.get('type', task_type),
                            "itemId": item['itemId']
                        }
                        res = await self.request(session, 'smt_newFission_doAssignment', params)
                        if res.get('subCode', '999') == '2':
                            break
                        await asyncio.sleep(0.5)
                elif task_type == '2':
                    println('{}, 助力码:{}!'.format(self.account, task['assistId']))
                    Code.insert_code(code_key=CODE_KEY, code_val=task['assistId'],
                                     account=self.account, sort=self.sort)


if __name__ == '__main__':
    from utils.process import process_start
    process_start(JdGrabBean, '限时抢京豆', help=False)
