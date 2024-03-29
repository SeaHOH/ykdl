# -*- coding: utf-8 -*-

from .._common import *
from .._byted import generate_mstoken, sign_xbogus


class Douyin(Extractor):
    name = '抖音 (Douyin)'

    def prepare_mid(self):
        return match1(self.url, r'\b(?:video/|music/|note/|vid=|aweme_id=|item_ids=)(\d+)')

    def prepare(self):
        info = MediaInfo(self.name)

        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        params = {
            'aweme_id': self.mid,
            'aid': 6383,
            'version_name': '23.5.0',
            'device_platform': 'webapp',
            'os_version': 10
        }
        params['X-Bogus'] = sign_xbogus(urlencode(params), ua)
        data = get_response('https://www.douyin.com/aweme/v1/web/aweme/detail/',
                            params=params,
                            headers={
                                'User-Agent': ua,
                                'Cookie': {'msToken': generate_mstoken()},
                                'Referer': 'https://www.douyin.com/'
                            }).json()
        assert data['status_code'] == 0, data['status_msg']
        assert data['aweme_detail'], data['filter_detail']

        data = data['aweme_detail']
        aweme_type = data['aweme_type']
        # TikTok [0, 51, 55, 58, 61, 150]
        if aweme_type not in [2, 68, 150, 0, 4, 51, 55, 58, 61]:
            print('new type', aweme_type)
        music_image = aweme_type in [2, 68, 150]  # video [0, 4, 51, 55, 58, 61]
        title = data['desc']
        nickName = data['author'].get('nickname', '')
        uid = data['author'].get('unique_id') or \
                data['author']['short_id']

        info.title = '{title} - {nickName}(@{uid})'.format(**vars())
        info.artist = nickName
        info.duration = data['duration'] // 1000

        ext = 'mp4'
        url = data['video']['play_addr']['url_list'][0] \
                        .replace('playwm', 'play')
        if music_image or 'music' in url:
            ext = 'mp3'
            url = data['video']['cover']['url_list'][0], url
        info.streams['current'] = {
            'container': ext,
            'profile': data['video']['ratio'].upper(),
            'src': [url]
        }
        return info

site = Douyin()
