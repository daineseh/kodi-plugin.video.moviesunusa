#-*- coding: utf-8 -*-
import sys
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import youtube_dl

from clawler import ParseMovieSunUSA


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def page_number(url):
    return url.split('-')[-1].split('.')[0]

mode = args.get('mode', None)

if mode is None:
    obj = ParseMovieSunUSA()

    li = xbmcgui.ListItem('[COLOR red]熱門美劇[/COLOR]')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=None, listitem=li, isFolder=False)

    for series in obj.get_hot():
        url = build_url({'mode': 'episodes', 'folder_name': series.url})
        li = xbmcgui.ListItem(series.name)
        li.setArt({'thumb': series.thumb, 'icon': series.thumb, 'fanart': series.thumb})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

    li = xbmcgui.ListItem('[COLOR yellow]最新美劇[/COLOR]')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=None, listitem=li, isFolder=False)

    for series in obj.new_arrivals():
        url = build_url({'mode': 'episodes', 'folder_name': series.url})
        li = xbmcgui.ListItem(series.name)
        li.setArt({'thumb': series.thumb, 'icon': series.thumb, 'fanart': series.thumb})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

    li = xbmcgui.ListItem('[COLOR yellow]劇集列表[/COLOR]')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=None, listitem=li, isFolder=False)
    url = build_url({'mode': 'list', 'folder_name': 1})
    li = xbmcgui.ListItem('A - G')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    url = build_url({'mode': 'list', 'folder_name': 2})
    li = xbmcgui.ListItem('H - R')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    url = build_url({'mode': 'list', 'folder_name': 3})
    li = xbmcgui.ListItem('S - Z')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'list':
    id = args['folder_name'][0]
    obj = ParseMovieSunUSA()

    if id == '1':
        content = obj.list_of_part1()
    elif id == '2':
        content = obj.list_of_part2()
    elif id == '3':
        content = obj.list_of_part3()
    for tag, lists in content.iteritems():
        li = xbmcgui.ListItem('[COLOR yellow]%s[/COLOR]' % tag)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=None, listitem=li, isFolder=False)
        for series in lists:
            url = build_url({'mode': 'episodes', 'folder_name': series.url})
            li = xbmcgui.ListItem(series.name)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'episodes':
    url = args['folder_name'][0]
    obj = ParseMovieSunUSA(url)

    for series in obj.get_episodes():
        url = build_url({'mode': 'resource', 'folder_name': series.url, 'thumb': series.thumb})
        li = xbmcgui.ListItem(series.name)
        li.setArt({'thumb': series.thumb, 'icon': series.thumb, 'fanart': series.thumb})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'resource':
    url = args['folder_name'][0]
    thumb = args['thumb'][0]
    obj = ParseMovieSunUSA(url)

    for idx, source in enumerate(obj.get_films(), start=1):
        url = build_url({'mode': 'play', 'folder_name': source})
        domain = urlparse.urlparse(source).netloc
        li = xbmcgui.ListItem('[COLOR white]%s.%s[/COLOR]' % (idx, domain))
        li.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'play':
    url = args['folder_name'][0]

    opts = {
        'forceurl': True,
        'quiet': True,
        'simulate': True,
    }

    with youtube_dl.YoutubeDL(opts) as ydl:
        resource_uri = ydl.extract_info(url).get('url')
        if not resource_uri:
            entries = ydl.extract_info(url).get('entries')
            resource_uri = entries[-1].get('url')
    xbmc.Player().play(resource_uri)

