import re
from flask import *
import requests
import logging as log
import io


log.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=log.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

pas = Flask(__name__)

"""正则表达式预编译区begin"""
ytb2mp3_recompile_1 = re.compile(r'v=\w+')
ytb2mp3_recompile_2 = re.compile(r'''k__id\s+=\s+(["'])(.*?)\1''')
ytb2mp3_recompile_3 = re.compile(r"""<a\s+(?:[^>]*?\s+)?href=(["'])(.*?)\1""")
"""正则表达式预编译区end"""

headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-MO;q=0.7,zh;q=0.6'
    }

def getY2Mate(link):
    r = requests.get(url=link, headers=headers)
    log.debug(r.status_code)
    return r.content, r.headers.get("content-length")


@pas.route('/ytb2mp3', methods=['GET', 'POST', 'OPTIONS'])
def ytb2mp3():
    # try:
        videoId = request.values.get('vid')
        # videoId = videoId[:-4]
        log.info('videoId: {}'.format(videoId))
        p = {
            'url': f'https://www.youtube.com/watch?v={videoId}',
            'q_auto': 0,
            'ajax': 1
        }
        response = requests.post("https://www.y2mate.com/mates/en249/analyze/ajax", p, headers=headers, timeout=10).json()
        # log.error('request post error: https://www.youtube.com/watch?v={}'.format(videoId))
        _id = re.search(ytb2mp3_recompile_2, response['result']).group().strip('''k__id = "''').strip('''"''')
        log.info('_id {}'.format(_id))
        p2 = {
            'type': 'youtube',
            '_id': _id, 
            'v_id': videoId,
            'ajax': 1,
            'token': '',
            'ftype': 'mp3',
            'fquality': 128
        }
        response = requests.post("https://www.y2mate.com/mates/convert", p2, headers=headers, timeout=10).json()["result"]
        log.info('response:  {}'.format(response))
        music_link=re.search(ytb2mp3_recompile_3, response).group().strip('''<a href=''').strip('''"''')
        log.info('music_link: {}'.format(music_link))
        c, l = getY2Mate(music_link)
        response = send_file(io.BytesIO(c), mimetype='audio/mpeg')
        response.headers['Content-Type'] = 'audio/mpeg'
        response.headers['Content-Length'] = l
        return response
    # except:
    #     log.error('parse error')
    #     return json.dumps({'error': 0})

if __name__ == '__main__':
    log.info('服务器准备启动...')
    log.info('アトリは、高性能ですから!')
    pas.run(host='127.0.0.1', port=6705, debug=True)
    # pas.run(host='0.0.0.0', port=6705, debug=True)