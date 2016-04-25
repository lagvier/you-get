#!/usr/bin/env python
__all__ = ['kissanime_download', 'kissanime_download_playlist']

from ..common import *
import cfscrape
import base64
from multiprocessing import Process
import itertools, sys

scraper = cfscrape.create_scraper()
spinner = itertools.cycle(['-', '/', '|', '\\'])

def toggle(num):
    while num > 0:
        sys.stdout.write(next(spinner))  # write the next character
        sys.stdout.flush()               # flush stdout buffer (actual character display)
        sys.stdout.write('\b')           # erase the last written char

def get_title(html):
    btitle = re.search(b'<title>(.*)</title>', html, flags=re.DOTALL).group(1)
    title = ' '.join(str.join(" ", re.search(' (.*)-', btitle.decode('UTF-8'), flags=re.DOTALL).group(1).strip('\t, \r, \n').splitlines()).split())

    return title

def kissanime_download(url, s=False, output_dir='.', merge=True, info_only=False, **kwargs):
    if ' ' in url:
        search = url.split(' ',1)[1]
        url = ("https://kissanime.to/Search/Anime/" + search)
        search = True
    else:
        search = False
    p = Process(target = toggle, args=(1,))
    p.start()
    html = scraper.get(url).content
    p.terminate()
    sys.stdout.write('\b')
    if search:
        kissanime_download_search(html, output_dir, merge, info_only, **kwargs)
    elif "id=" not in url.lower():
        kissanime_download_playlist(html, s, output_dir, merge, info_only, **kwargs)
    else:
        url = kissanime_url(html)
        title = get_title(html)
        if 'stream_id' in kwargs and kwargs['stream_id']:
            # Extract the stream
            stream_id = int(kwargs['stream_id'])
            if stream_id > len(url) or int(stream_id) <= 0:
                log.e('[Error] Invalid format id.')
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

def kissanime_download_playlist(html, search=False, output_dir='.', merge=True, info_only=False, **kwargs):
    playlist = re.sub( '\s+', ' ', (re.search(b'<table class="listing">(.*)</table>', html, flags=re.DOTALL).group(1).decode('UTF-8'))).strip()
    links = re.findall(u'<a href="([^."]+)', playlist)
    if search:
        url_list = []
        print()
        for idx, link in enumerate(links):
            url = 'https://kissanime.to' + link
            url_list.append(url)
            html = scraper.get(url).content
            print('[ '+ str(len(links)-idx) +' ] __________________________________')
            print('dl-with: you-get --format='+str(len(links)-idx)+' [url]')
            url = kissanime_url(html)[0]
            title = get_title(html)
            type, ext, size = url_info(url, faker=True)
            print_info(site_info, title, type, size)
        input_var = input("Which episode(s) did you want to get: ")
        if "-" not in input_var:
            stream_id = int(input_var)
            if stream_id > len(links) or int(stream_id) <= 0:
                log.e('[Error] Invalid format id.')
                exit(2)
            url = 'https://kissanime.to' + links[len(links)-stream_id]
            html = scraper.get(url).content
            url = kissanime_url(html)[0]
            title = get_title(html)
            type, ext, size = url_info(url, faker=True)
            print_info(site_info, title, type, size)

            if not info_only:
                download_urls([url], title, ext, size, output_dir, merge)
        else:
            stream_id_range = input_var.partition('-')
            if int(stream_id_range[2]) > len(links) or int(stream_id_range[0]) <= 0 or int(stream_id_range[0]) > int(stream_id_range[2]):
                log.e('[Error] Invalid format id range.')
                exit(2)
            for x in range(int(stream_id_range[2]), int(stream_id_range[0])-1, -1):
                url = 'https://kissanime.to' + links[len(links)-x]
                html = scraper.get(url).content
                url = kissanime_url(html)[0]
                title = get_title(html)
                type, ext, size = url_info(url, faker=True)
                print_info(site_info, title, type, size)

                if not info_only:
                    if x == int(stream_id_range[2]):
                        print("The download bar may look weird, but its fine. The console is just trying to update the same progress bar for multiple downloads.")
                    elif x == int(stream_id_range[0]):
                        print("The download bar may look weird, but its fine.")
                    p = Process(target = download_urls, args=([url], title, ext, size, output_dir, merge))
                    p.start()
    else:
        if 'stream_id' in kwargs and kwargs['stream_id']:
            # Extract the stream
            if "-" not in kwargs['stream_id']:
                stream_id = int(kwargs['stream_id'])
                if stream_id > len(links) or int(stream_id) <= 0:
                    log.e('[Error] Invalid format id.')
                    exit(2)
                url = 'https://kissanime.to' + links[len(links)-stream_id]
                html = scraper.get(url).content
                url = kissanime_url(html)[0]
                title = get_title(html)
                type, ext, size = url_info(url, faker=True)
                print_info(site_info, title, type, size)

                if not info_only:
                    download_urls([url], title, ext, size, output_dir, merge)
            else:
                stream_id_range = kwargs['stream_id'].partition('-')
                if int(stream_id_range[2]) > len(links) or int(stream_id_range[0]) <= 0 or int(stream_id_range[0]) > int(stream_id_range[2]):
                    log.e('[Error] Invalid format id range.')
                    exit(2)
                for x in range(int(stream_id_range[2]), int(stream_id_range[0])-1, -1):
                    url = 'https://kissanime.to' + links[len(links)-x]
                    html = scraper.get(url).content
                    url = kissanime_url(html)[0]
                    title = get_title(html)
                    type, ext, size = url_info(url, faker=True)
                    print_info(site_info, title, type, size)

                    if not info_only:
                        if x == int(stream_id_range[2]):
                            print("The download bar may look weird, but its fine. The console is just trying to update the same progress bar for multiple downloads.")
                        elif x == int(stream_id_range[0]):
                            print("The download bar may look weird, but its fine.")
                        p = Process(target = download_urls, args=([url], title, ext, size, output_dir, merge))
                        p.start()

        else:
            for idx, link in enumerate(links):
                url = 'https://kissanime.to' + link
                html = scraper.get(url).content
                print('dl-with:    you-get --format='+str(len(links)-idx)+' [url]')
                url = kissanime_url(html)[0]
                title = get_title(html)
                type, ext, size = url_info(url, faker=True)
                print_info(site_info, title, type, size)

def kissanime_download_search(html, output_dir='.', merge=True, info_only=False, **kwargs):
    playlist = re.sub( '\s+', ' ', (re.search(b'<table class="listing">(.*)</table>', html, flags=re.DOTALL).group(1).decode('UTF-8'))).strip()
    links = re.findall(u'<a href="([^."]+)', playlist)
    url_list = []
    for idx, link in enumerate(links):
        if (idx < 10):
            url = 'https://kissanime.to' + link
            url_list.append(url)
            print(str(idx+1) + '. ' + url)
        else:
            print('10+ items not listed.')
    input_var = input("Which anime did you want to get: ")
    if "-" not in input_var:
        stream_id = int(input_var)
        if stream_id > len(url_list) or int(stream_id) <= 0:
            log.e('[Error] Invalid format id.')
            exit(2)
        kissanime_download(url_list[int(input_var)-1], True, output_dir, merge, info_only, **kwargs)
    else:
        stream_id_range = input_var.partition('-')
        if int(stream_id_range[2]) > len(url_list) or int(stream_id_range[0]) <= 0 or int(stream_id_range[0]) > int(stream_id_range[2]):
            log.e('[Error] Invalid format id range.')
            exit(2)
        for x in range(int(stream_id_range[2]), int(stream_id_range[0])-1, -1):
            kissanime_download(url_list[int(x)-1], True, output_dir, merge, info_only, **kwargs)


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
