#!/usr/bin/env python
__all__ = ['kissanime_download', 'kissanime_download_playlist']

from ..common import *
import cfscrape
import base64

scraper = cfscrape.create_scraper()

def get_title(html):
    btitle = re.search(b'<title>(.*)</title>', html, flags=re.DOTALL).group(1)
    title = ' '.join(str.join(" ", re.search(' (.*)-', btitle.decode('UTF-8'), flags=re.DOTALL).group(1).strip('\t, \r, \n').splitlines()).split())

    return title

def kissanime_download(url, output_dir='.', merge=True, info_only=False, **kwargs):
    html = scraper.get(url).content
    if "episode-" not in url.lower():
        kissanime_download_playlist(html, output_dir, merge, info_only, **kwargs)
    else:
        url = kissanime_url(html)
        title = get_title(html)
        if 'stream_id' in kwargs and kwargs['stream_id']:
            # Extract the stream
            stream_id = int(kwargs['stream_id'])
            if stream_id > len(url) or int(stream_id) <= 0:
                log.e('[Error] Invalid id.')
                exit(2)
            url = url[len(url)-stream_id]
            type, ext, size = url_info(url, faker=True)
            print_info(site_info, title, type, size)

        else:
            if info_only:
                for idx, link in enumerate(url):
                    if idx == 0:
                        print('[ DEFAULT ] __________________________________')
                    print('dl-with:    you-get --format='+str(len(url)-idx)+' [url]')
                    type, ext, size = url_info(link, faker=True)
                    print_info(site_info, title, type, size)
            else:
                title = get_title(html)
                type, ext, size = url_info(url[0], faker=True)
                print_info(site_info, title, type, size)
            url = url[0]

        if not info_only:
            download_urls([url], title, ext, size, output_dir, merge=merge)

def kissanime_download_playlist(html, output_dir='.', merge=True, info_only=False, **kwargs):
    playlist = re.sub( '\s+', ' ', (re.search(b'<table class="listing">(.*)</table>', html, flags=re.DOTALL).group(1).decode('UTF-8'))).strip()
    links = re.findall(u'<a href="([^."]+)', playlist)
    if 'stream_id' in kwargs and kwargs['stream_id']:
        # Extract the stream
        stream_id = int(kwargs['stream_id'])
        if stream_id > len(links) or int(stream_id) <= 0:
            log.e('[Error] Invalid id.')
            exit(2)
        url = 'https://kissanime.to' + links[len(links)-stream_id]
        html = scraper.get(url).content
        url = kissanime_url(html)[0]
        title = get_title(html)
        type, ext, size = url_info(url, faker=True)
        print_info(site_info, title, type, size)

        if not info_only:
            download_urls([url], title, ext, size, output_dir, merge=merge)

    else:
        for idx, link in enumerate(links):
            url = 'https://kissanime.to' + link
            html = scraper.get(url).content
            print('dl-with:    you-get --format='+str(len(links)-idx)+' [url]')
            url = kissanime_url(html)[0]
            title = get_title(html)
            type, ext, size = url_info(url, faker=True)
            print_info(site_info, title, type, size)

def kissanime_url(html):
    selectQuality = re.search(b'<select id="selectQuality">.*</select>', html).group(0)
    options = re.findall(b'<option value="([^"]+)', selectQuality)
    if options:
        url = ""
        for val in options:
            url += "\n"+base64.b64decode(val).decode("UTF-8")
    url_list = [y for y in (x.strip() for x in url.splitlines()) if y]
    return url_list


site_info = "KissAnime.to"
download = kissanime_download
download_playlist = kissanime_download_playlist
