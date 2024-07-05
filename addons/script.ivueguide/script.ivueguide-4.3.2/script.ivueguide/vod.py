import xbmc, xbmcgui, json, re, datetime, time
try: import urllib.request as urlrequest
except: import urllib2 as urlrequest
try:import urllib.parse as urlparse
except: import urllib as urlparse

dialog = xbmcgui.Dialog() 

def flash_iptv(chan, program, progTitle):
    return subVod(chan, program, progTitle, 'flashiptv')
    
def simply_tv(chan, program, progTitle):
    return subVod(chan, program, progTitle, 'simplytv')

def ohm_media(chan, program, progTitle):
    chan=chan.replace('BBC One','bbc1')
    chan=chan.replace('BBC Two','bbc2')
    chan=chan.replace('BBC Two','bbc2')
    chan=chan.replace('NickJr','Nick Junior')
    chan=chan.replace('Chart Show TV','Chart Show')
    chan=chan.replace('Sky Cinema Action','Sky Action')
    chan=chan.replace('Sky Cinema Comedy','Sky Comedy')
    chan=chan.replace('Sky Cinema Thriller','Sky Crime Thriller')
    chan=chan.replace('Sky Cinema Family','Sky Family')
    chan=chan.replace('Sky Cinema Greats','Sky Greats')
    chan=chan.replace('Sky Cinema Drama','Sky Drama')
    if chan in ['RTE One', 'RTE Two', 'TG4', 'UTV']:
        tag = '.ie'
    else:
        tag = '.uk'
    if chan == 'Pick':
        chan = 'Pick TV'
    elif chan == 'DMAX':
        chan = 'Discovery Dmax'
    elif chan == 'Watch':
        chan = 'W'
    elif chan == 'CI':
        chan = 'Crime And Investigation Network'
    elif chan == 'ID':
        chan = 'Investigation Discovery'
    elif chan == 'Kiss':
        chan = 'Kiss TV'
    return subVod(chan.lower().replace(' ','')+tag, program, progTitle, 'OHMMediaPlus')

def subVod(chan, program, progTitle, addon):
    found = None
    if addon == 'OHMMediaPlus':
        queryThis = "plugin://plugin.video.%s/?url=url&mode=13&name=Catchup+TV&iconimage=&description=" % (addon)
    else:
        queryThis = "plugin://plugin.video.%s/?action=vod_channels&extra&page&plot&thumbnail=&title=CatchUp&url" % (addon)
    checkthisurl = ('{"jsonrpc":"2.0", "method":"Files.GetDirectory", "params":{"directory":"%s"}, "id": 1}' % queryThis)
    checkthisurltoo = ('{"jsonrpc":"2.0", "method":"Files.GetDirectory", "params":{"directory":"%s"}, "id": 1}')

    respond = xbmc.executeJSONRPC(checkthisurl)
    tvarchive = json.loads(respond)
    result   = tvarchive['result'] 
    ArchiveResult = result['files']    

    for channel in ArchiveResult:
        foundChannel = channel['label']
        cleanTitle = foundChannel #.rsplit('[/B]', 1)[0].split('[B]', 1)[-1]
        path  = channel['file']
        if foundChannel == str(chan):
            found = path
            break

    if not found == None:
        response = xbmc.executeJSONRPC(checkthisurltoo % (found))
        content = json.loads(response)
        result   = content['result'] 
        ChannelsResult = result['files']    

        for archive in ChannelsResult:
            foundChannel = archive['label']
            cleanTitle = foundChannel.rsplit('[/B]', 1)[0].split('[B]', 1)[-1]
            cleanTitle = cleanTitle.replace('[COLOR white]','').replace('[/COLOR]','')
            stream  = archive['file']
            if cleanTitle == str(program):
                return stream
                break

    else:
        yes_pressed=dialog.yesno('[COLOR ffff7e14][B]iVue On Demand[/B][/COLOR]', 'Couldnt find ' +progTitle+ ' Would u like to search other addons?',nolabel='Cancel',yeslabel='Search')
        if yes_pressed:
            return 'Search'
        else:
            return None
            
def itv_player(chan, program, progTitle, search=None):
    cleanProgram = str(progTitle.replace(':','').replace("'","").replace(' ', '-').replace('&amp;', '&')).lower()
    items = []
    match = ''
    path = None
    programItv = ''
    itvcode = ''
    searchITV = '%s itvhub' % progTitle
    quoteurl = urlparse.quote(searchITV)
    itvurl = 'https://www.google.co.uk/search?q=%s' % quoteurl
    req = urlrequest.Request(itvurl)
    req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urlrequest.urlopen(req)
    link=response.read().decode('utf-8')
    response.close()
    gResult = re.compile('href="(.*?)"',re.DOTALL).findall(link)
    for site in gResult:
        if 'itv.com/hub/' in site:
            programItv = site.split('hub/')[1].split('/')[0]
            itvcode = site.split('hub/')[1]
            itvcode = itvcode.split('&')[0]
            break
    pluginurl = "plugin://plugin.video.itv/?iconimage=&mode=2&name="+programItv+"&url=https%3a%2f%2fwww.itv.com%2fhub%2f"+itvcode            
    if not itvcode == '' and search == None:
        checkthisurl = ('{"jsonrpc":"2.0", "method":"Files.GetDirectory", "params":{"directory":"%s"}, "id": 1}')
        respond = xbmc.executeJSONRPC(checkthisurl % (pluginurl))
        tvarchive = json.loads(respond)
        result   = tvarchive['result'] 
        ArchiveResult = result['files']
        for channel in ArchiveResult:
            foundChannel = channel['label']
            title = foundChannel.split(' - ')[1].replace('AM','').replace('PM','').replace(' ',' - ')
            cleanDate = datetime.datetime.strptime(title.split(' - ')[0], '%d/%m/%Y').strftime('%Y-%m-%d')
            itvtime = datetime.datetime.strptime(title.split(' - ')[1], '%H:%M')
            if '-' in str(time.strftime("%z")):
                timeDiff = time.strptime(str(time.strftime("%z").replace('-','')),'%H%M')
                formatTime = itvtime - datetime.timedelta(minutes=timeDiff.tm_min, hours=timeDiff.tm_hour)
                newTime = formatTime.time().strftime('%H:%M')
            elif '+' in str(time.strftime("%z")):
                timeDiff = time.strptime(str(time.strftime("%z").replace('+','')),'%H%M')
                formatTime = itvtime + datetime.timedelta(minutes=timeDiff.tm_min, hours=timeDiff.tm_hour)
                newTime = formatTime.time().strftime('%H:%M')
            else:
                newTime = itvtime
            cleanTitle = cleanDate + ' - ' + str(newTime)
            found  = channel['file']
            items.append(cleanTitle)
            if cleanTitle == str(program):
                match = cleanTitle
                path = found
                return path
                break

    if path == None:
        if len(items) > 0 or search != None:
            xbmc.executebuiltin('ActivateWindow(10025,'+pluginurl+',return)')
            return None
        else:
            yes_pressed = dialog.yesno('[COLOR ffff7e14][B]iVue On Demand[/B][/COLOR]', 'Couldnt find ' +cleanProgram+ ' Would u like to search other addons?',nolabel='Cancel',yeslabel='Search')
            if yes_pressed:
                return 'Search'
            else:
                return None
                
def iplayer_itv_player(chan, program, progTitle):
    bbc = ['BBC One', 'BBC Two', 'BBC FOUR', 'BBC One North Ireland', 'BBC One Scotland', 'BBC One Wales', 'CBeebies', 'CBBC', 'BBC News', 'BBC Alba', 'S4C']
    itv = ['ITV1', 'ITVBe', 'ITV2', 'ITV3', 'ITV4', 'ITV1 +1', 'ITV2 +1', 'ITV3 +1', 'ITV4 +1', ]
    if str(chan) in bbc:
        plugin = iplayer(chan, program, progTitle)
        return plugin
    elif str(chan) in itv:
        plugin = itv_player(chan, program, progTitle)
        return plugin
    else:
        return 'Search'

    
    
def iplayer(chan, program, progTitle):
    gotlink = False
    num = 0
    cleanProgram = str(progTitle.replace("'","").replace(' ', '-').replace('&amp;','&')).lower()
    finalResults = []
    if ':' in cleanProgram:
    	cleanProgram = cleanProgram.split(':')[0]
    quoteurl = urlparse.quote(cleanProgram)
    bbcurl = 'https://www.bbc.co.uk/iplayer/search?q=%s' % quoteurl
    link = getfiles(bbcurl)
    lastSearch = re.compile('aria-label=".*?" href="/iplayer/episode/(.*?)"',re.DOTALL).findall(link)
    for ep in lastSearch:
        finalResults.append(ep)
    try:
        sResult = re.compile('href="/iplayer/episodes/(.*?)"',re.DOTALL).findall(link)
        for series in sResult:
            surl = 'https://www.bbc.co.uk/iplayer/episodes/' + series
            episodes = getfiles(surl)
            epResult = re.compile('aria-label=".*?" href="/iplayer/episode/(.*?)"',re.DOTALL).findall(episodes)
            for result in epResult:
                num += 1
                if num < 7:
            	    finalResults.append(result)
                else:
                    break
    except:
        pass
    for item in finalResults:
        epurl = 'https://www.bbc.co.uk/iplayer/episode/' + item 
        episodelink = getfiles(epurl)
        epAir = re.compile('<span class="tvip-hide">First shown</span><span class="episode-metadata__text">(.*?)</span>',re.DOTALL).findall(episodelink)
        for when in epAir:
            eptime = when.split(' ')[0]
            try:
                epdate = when.split('m ')[1]
            except:
                epdate = when
            try:
                timeDiff = datetime.datetime.strptime(eptime, '%I%p')
                timeDiff = datetime.datetime.strftime(timeDiff, '%H:%M')
            except:
                try:
                    timeDiff = datetime.datetime.strptime(eptime, '%I:%M%p')
                    timeDiff = datetime.datetime.strftime(timeDiff, '%H:%M')
                except:
                    timeDiff = ''

            cleanDate = datetime.datetime.strptime(epdate, '%d %b %Y').strftime('%Y-%m-%d')
            found = str(cleanDate + ' - ' + timeDiff)
            if found == str(program):
                gotlink = True
                url = 'plugin://plugin.video.iplayerwww/?url=%s&mode=202&name=&iconimage=&description=&subtitles_url=&logged_in=False' % epurl
                return url
                break

    if gotlink == False:
        if len(finalResults) > 0:
            xbmc.executebuiltin("ActivateWindow(10025,plugin://plugin.video.iplayerwww/?mode=104&url=url&keyword=%s,return)" % quoteurl)
            return None
        else:
            yes_pressed = dialog.yesno('[COLOR ffff7e14][B]iVue On Demand[/B][/COLOR]', 'Couldnt find ' +cleanProgram+ ' Would u like to search other addons?',nolabel='Cancel',yeslabel='Search')
            if yes_pressed:
                return 'Search'
            else:
                return None
                
def getfiles(url):
    req = urlrequest.Request(url)
    #req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urlrequest.urlopen(req)
    link=response.read().decode('utf-8')
    response.close()
    return link