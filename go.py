import json
import re
import time
from pyparsing import WordEnd
import requests
from werkzeug._reloader import run_with_reloader
import logging as log
log.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=log.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import start_webhook

from config import *

WEBHOOK_PATH = f'/{API_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

"""
start - 开机
what - 什么
why - 为什么
music - 搜歌
bhot - b站热搜
whot - 微博热搜
e2c - 英语翻译
"""

def getYoutube(videoId):
    try:
        p = {
            'url': f'https://www.youtube.com/watch?v={videoId}',
            'q_auto': 0,
            'ajax': 1
        }
        response = requests.post("https://www.y2mate.com/mates/en249/analyze/ajax", p, timeout=3).json()
        _id = re.search(r'''k__id\s+=\s+(["'])(.*?)\1''', response['result']).group().strip('''k__id = "''').strip('''"''')
        p2 = {
            'type': 'youtube',
            '_id': _id, 
            'v_id': videoId,
            'ajax': 1,
            'token': '',
            'ftype': 'mp3',
            'fquality': 128
        }
        response = requests.post("https://www.y2mate.com/mates/convert", p2, timeout=3).json()["result"]
        music_link=re.search(r"""<a\s+(?:[^>]*?\s+)?href=(["'])(.*?)\1""",response).group().strip('''<a href=''').strip('''"''')
        return music_link
    except:
        return None

@dp.inline_handler()
async def inlinec(message: types.InlineQuery):
    # aid = message['id']
    word = message['query']
    log.info(word)
    results = []
    if len(word) <= 3:
        await message.answer(
            results = results,
        )
    elif word[0:2] == 'ms':
        word = word[2:].strip()
        try:
            params = {
                "hlpretag": "",
                "hlposttag": "",
                "s": word,
                "type": 1,
                "offset": 0,
                "total": True,
                "limit": 20
            }
            r = requests.post("http://music.163.com/api/search/get/web?csrf_token=", params, timeout=3, proxies=PROXIES_CN).json()
            ranklink = r['result']['songs']
            log.info('succeed')
        except:
            log.info("Failed to")
            await message.answer(
                results = results,
            )
        else:
            n = 0
            for i in ranklink:
                if n == 10:
                    break
                try:
                    try:
                        response = requests.get("http://music.163.com/song/media/outer/url?id={}.mp3".format(i['id']), timeout=3, allow_redirects=False, proxies=PROXIES_CN)
                        headers = dict(response.headers)
                        url = headers['Location']
                    except:
                        continue
                    else:
                        results.append(
                            types.InlineQueryResultAudio(
                                id = i['id'],
                                audio_url = url,
                                title = i['name'],
                                performer = i['artists'][0]['name'],
                                # caption = i['name'] + '  -  ' + i['artists'][0]['name']
                            )
                        )
                        n += 1
                except:
                    continue
            await message.answer(
                results = results,
                cache_time = 0
            )
    elif word[0:3] == 'yms':
        query = word[3:].strip()
        log.info(query)
        # results.append(
        #         types.InlineQueryResultAudio(
        #             id = 'xxxx',
        #             audio_url = 'https://jellyqwq.com/music/8xg3vE8Ie_E.mp3',
        #             title = 'love story',
        #             performer = 'Taylor Swift',
        #             # caption = i['name'] + '  -  ' + i['artists'][0]['name']
        #         )
        #     )
        data = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20220617.00.00",
                }
            },
            "query": f"{query}",
        }
        try:
            response = requests.post('https://www.youtube.com/youtubei/v1/search', json=data, timeout=3).json()
            contents = response['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
            # n = 0
            for c in contents:
                # if n == 10:
                #     break
                if 'videoRenderer' in c:
                    videoRenderer = c['videoRenderer']
                    videoId = videoRenderer['videoId']
                    try:
                        title = videoRenderer['title']['runs'][0]['text']
                        performer = videoRenderer['ownerText']['runs'][0]['text']
                        results.append(
                            types.InlineQueryResultAudio(
                                id = videoId,
                                # audio_url = f'http://124.156.210.60:6705/ytb2mp3?vid={videoId}.mp3',
                                audio_url = 'http://youtube.mp3.jellyqwq.com/ytb2mp3?vid={}.mp3'.format(videoId),
                                title = title,
                                performer = performer,
                                # caption = i['name'] + '  -  ' + i['artists'][0]['name']
                            )
                        )
                        log.info('http://youtube.mp3.jellyqwq.com/ytb2mp3?vid={}.mp3'.format(videoId))
                        # n += 1
                    except:
                        continue
                else:
                    continue
            await message.answer(
                results = json.dumps(results),
                cache_time = 0
            )
        except:
            await message.answer(
                results = results,
                cache_time = 0
            )
    else:
        await message.answer(
            results = results,
            cache_time = 0
        )

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("你好, 旅行者!")


@dp.message_handler(commands=['what'])
async def send_welcome(message: types.Message):
    _m = message.text[len('/what')+16:]
    await message.answer(f'https://www.google.com/search?q={_m}')


@dp.message_handler(regexp='派蒙生日')
async def paimon_photo(message: types.Message):
    with open('2020PaimonBirthday.png', 'rb') as photo:
        await message.reply_photo(photo, '这是我2020年6月1日生日的照片噢')


@dp.message_handler(commands=['bhot'])
async def bhot(message: types.Message):
    try:
        url = 'http://s.search.bilibili.com/main/hotword'
        response = requests.get(url).json()
        if response['code'] == 0:
            log.info('Get hot search success')
            timestamp = response['timestamp']
            HotWordTime = time.strftime("%Y-%m-%d %H:%M %a", time.localtime(timestamp))
            HotWordLsit =[]
            for li in response['list']:
                if li['word_type'] == 5:
                    word_type = '🔥'
                elif li['word_type'] == 4:
                    word_type = '⤴️'
                else:
                    word_type = ''
                HotWordLsit.append([li['pos'], li['keyword'], word_type]) # word_type 1:normal 4:new 5:hot
            _m = HotWordTime
            for i in HotWordLsit:
                _m += '\n'
                _m += str(i[0])
                _m += '.'
                _m += i[1]
                _m += '\t'
                _m += i[2]
        await message.answer(_m)
    except:
        await message.answer("🐭🐭我啊,没热搜啦")


@dp.message_handler(commands=['whot'])
async def bhot(message: types.Message):
    try:
        r = requests.get('https://weibo.com/ajax/side/hotSearch')
        data = r.json()['data']
        hotgov = data['hotgov']
        HotWordLsit = [['Top', hotgov['word'], hotgov['icon_desc']]]
        realtime = data['realtime']
        num = 1
        HotWordTime = time.strftime("%Y-%m-%d %H:%M %a", time.localtime(time.time()))
        for hot_dict in realtime:
            if 'label_name' in hot_dict.keys():
                HotWordLsit.append([str(num), hot_dict['word'], hot_dict['label_name']])
                num += 1
        _m = HotWordTime
        try:
            nc = int((message.text[len('/whot')+16:]).strip())
        except:
            nc = 10
        else:
            if 0 <= nc <= 50:
                pass
            else:
                nc = 10
        for n, i in enumerate(HotWordLsit, 0):
                _m += '\n'
                _m += i[0]
                _m += '.'
                _m += i[1]
                _m += '\t'
                temp = i[2]
                if temp == '沸':
                    _m += '🔥'
                elif temp == '新':
                    _m += '⤴️'
                else:
                    _m += ''
                if n == nc:
                    break
        await message.answer(_m)
    except:
        await message.answer("微博热搜404")


# @dp.message_handler(commands=['e2c'])
# async def e2c(message: types.Message):
#     try:
#         headers = {
#             'Cookie': 'JSESSIONID=abcAX3oajT_n6btH4tIfy; OUTFOX_SEARCH_USER_ID=-941548234@10.108.162.139; OUTFOX_SEARCH_USER_ID_NCOO=194331207.38996145; fanyi-ad-id=306808; fanyi-ad-closed=1; ___rl__test__cookies=1655231782511',
#             'Host': 'fanyi.youdao.com',
#             'Origin': 'https://fanyi.youdao.com',
#             'Referer': 'https://fanyi.youdao.com/',
#             'Sec-Fetch-Mode': 'cors',
#             'Sec-Fetch-Site': 'same-origin',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
#             'X-Requested-With': 'XMLHttpRequest',
#         }
#         word = message.text[len('/what')+16:]
#         data = {
#             'i': word,
#             'client': 'fanyideskweb',
#             'salt': '16552311696047',
#             'sign': '100b77ec92a88def43415f9edfa14ce9',
#             'keyfrom': 'fanyi.web',
#         }
#         _m = requests.post('https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule', headers=headers, data=data).json()['translateResult'][0]
#         await message.answer(word + '\n └─' + _m)
#     except:
#         await message.answer("translate 404")

async def on_shutdown(dp):
    log.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    log.warning('Bye!')


if __name__ == '__main__':
    run_with_reloader(
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    )
