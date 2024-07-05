#-*- coding: utf-8 -
import xbmc,xbmcvfs,xbmcplugin,xbmcaddon,xbmcgui,re,sys,os
import datetime,time, requests
import threading,collections
try: import Queue
except: import queue as Queue
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime as dtdeep
try: translatePath = xbmcvfs.translatePath
except: translatePath = xbmc.translatePath
pyver = sys.version_info[0]
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass
prnum=""
try:
    prnum= sys.argv[ 1 ]
except:
    pass


try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

myAddon = 'script.FreeVueGuide'
addonid = xbmcaddon.Addon(myAddon) 
runpath = translatePath(addonid.getAddonInfo('Path'))
userpath = translatePath(addonid.getAddonInfo('Profile'))
catChan = translatePath('special://profile/addon_data/plugin.video.IPTVsubscriber/custom_channels.ini')
setcats = addonid.getSetting('categories.path')
savepath = os.path.join(userpath, 'resources', 'xml_config')
defFile = os.path.join(runpath,'resources', 'xml', 'default.ini')
nameFile = os.path.join(savepath, 'name_change.ini')
userxml = os.path.join(userpath, 'user.xml')
myFile = os.path.join(savepath, 'channels.ini')
currentCats = os.path.join(userpath, 'resources', 'categories', setcats+'.ini')
tempCats = os.path.join(userpath, 'resources', 'categories', 'temp.ini')
testFile = os.path.join(savepath, 'test.txt')
chanlogo = os.path.join(runpath,'resources', 'png', 'iVuelogo_3.png')
ukflag = os.path.join(runpath,'resources', 'png', 'ukflag.png')
usflag = os.path.join(runpath,'resources', 'png', 'usflag.png')
canflag = os.path.join(runpath,'resources', 'png', 'canflag.png')
ausflag = os.path.join(runpath,'resources', 'png', 'ausflag.png')
dialog =  xbmcgui.Dialog()

try:
    os.stat(savepath)
except:
    os.makedirs(savepath)

if not os.path.exists(myFile):
    file = open(myFile, 'w+')
    file.close()


def config_p(ini_path):
    config = ConfigParser()
    config.optionxform = str
    try:config.read(ini_path, 'UTF-8')
    except: config.read(ini_path)
    return config
    
channelini = config_p(myFile)
defaultini = config_p(defFile)
nameini = config_p(nameFile)

def currentcatini():
    try:
        catini = config_p(currentCats)
    except:
        os.rename(currentCats, tempCats)
        catini = config_p(currentCats)
        oldfile = open(tempCats, 'r').readlines()
        for line in oldfile:
            if not '=' in line:
                continue
            key, val = line.strip().split('=')
            if not catini.has_section(val):
                catini.add_section(val)
            catini.set(val,key,val) 
        try:file = open(currentCats, 'w+', encoding='UTF-8')
        except:file = open(currentCats, 'w')
        catini.write(file)
        file.close()
        os.remove(tempCats)
    return catini
    
    
############### MAIN MENU####################

def main_menu():
	chanicon = os.path.join(runpath,'resources', 'png', 'chan.png')
	renameicon = os.path.join(runpath,'resources', 'png', 'rename.png')
	xmlicon = os.path.join(runpath,'resources', 'png', 'icon.png')
	menu = [xbmcgui.ListItem('Choose Channels','select channels from uk, us, ca', chanicon), xbmcgui.ListItem('Rename My Channels','change channel names for TV guide', renameicon), xbmcgui.ListItem('Make My TV Guide XML','build xml for Team FreeVueIPTV', xmlicon)]
	select = dialog.select('[COLOR fffea800]Main Menu[/COLOR]', menu, useDetails=True)
	
	if select == 0:
		channel_menu()
	if select == 1:
		channel_menu(rename=True)
	if select == 2:
		
		try:file = open(userxml, 'w+', encoding='utf8')
		except:file = open(userxml, 'w')
		xml_config(file)
		

############### CHANNEL MENU ####################

def channel_menu(rename=False, clear=False):
	uk = xbmcgui.ListItem('UK Channels')
	us = xbmcgui.ListItem('US Channels')
	can = xbmcgui.ListItem('Canada Channels')
	aus = xbmcgui.ListItem('Australia Channels')
	uk.setArt({'icon': ukflag})
	us.setArt({'icon': usflag})
	can.setArt({'icon': canflag})
	aus.setArt({'icon': ausflag})
	options = [uk, us, can, aus]
	select = dialog.select('[COLOR fffea800]iVue Channel Menu[/COLOR]', options, useDetails=True)
	
	if not select < 0:
		sec = options[select].getLabel().lower()
		
		showChan(sec)
		
		
############### USER MENU ####################

def user_menu(rename=False, chans=False, names=False):
	options = []
	if names == True:
	    inifile = nameFile
	    ini = nameini
	    channels = ini.sections()
	
	else:
	    inifile = myFile
	    ini = channelini
	    channels = ini.sections()
	
	if len(channels) == 0 and rename == False:
	    try: 
	        os.remove(inifile)
	        dialog.ok('iVue', 'file has been deleted. Thank you for using Team FreeVueIPTV')
	    except:
	        dialog.ok('iVue', 'Unable to delete file, this might be because there isnt one. Thank you for using Team FreeVueIPTV')
	    return
	elif len(channels) == 0 and rename == True:
	    dialog.ok('iVue', 'Please select some channels first as we cant seem to find any. Thank you for using Team FreeVueIPTV')
	    return
	if 'uk channels' in channels and len(ini.options('uk channels')) > 0:
	    uk = xbmcgui.ListItem('UK Channels')
	    uk.setArt({'icon': ukflag})
	    options.append(uk)
	if 'us channels' in channels and len(ini.options('us channels')) > 0:
	    us = xbmcgui.ListItem('US Channels')
	    us.setArt({'icon': usflag})
	    options.append(us)
	if 'canada channels' in channels and len(ini.options('canada channels')) > 0:
	    can = xbmcgui.ListItem('Canada Channels')
	    can.setArt({'icon': canflag})
	    options.append(can)
	if 'australia channels' in channels and len(ini.options('australia channels')) > 0:
	    aus = xbmcgui.ListItem('Australia Channels')
	    aus.setArt({'icon': ausflag})
	    options.append(aus)
	select = dialog.select('[COLOR fffea800]My Channel Menu[/COLOR]', options, useDetails=True)
	
	if not select < 0:
	    sec = options[select].getLabel().lower()
		
	    if chans == True:
		    channelini.remove_section(sec)
		    try:myfile = open(myFile, 'w+', encoding='utf8')
		    except:myfile = open(myFile, 'w')
		    channelini.write(myfile)
		    myfile.close()
		    dialog.ok('iVue', str(sec) +' have been removed. Thank you for using Team FreeVueIPTV')
		
	    elif names == True:
		    nameini.remove_section(sec)
		    try:nafile = open(nameFile, 'w+', encoding='utf8')
		    except:nafile = open(nameFile, 'w')
		    nameini.write(nafile)
		    nafile.close()
		    dialog.ok('iVue', str(sec) +' name changes have been removed. Thank you for using Team FreeVueIPTV')
		    
	    elif rename == True:
		    rename_chan(sec)
		
	    else:
		    showChan(sec)
		
		
############### RENAME ####################

def rename_chan(sec):
	new_names = []
	chanList = []
	if channelini.has_section(sec):
	    mylist = channelini.items(sec)
	    for item in mylist:
	        if nameini.has_option(sec, item[0]):
	            lis = xbmcgui.ListItem(nameini.get(sec, item[0]), '[COLOR fffea800]renamed [/COLOR]' + item[0])
	            lis.setArt({'icon': item[1].split(', ')[1]})
	            chanList.append(lis)
	            new_names.append([nameini.get(sec, item[0]), item[1], item[0], '[COLOR fffea800]renamed [/COLOR]' + item[0]])
	        else:
	            lis = xbmcgui.ListItem(item[0])
	            lis.setArt({'icon': item[1].split(', ')[1]})
	            chanList.append(lis)
	            new_names.append([item[0],item[1], item[0], ''])
	
	    #chanList = [xbmcgui.ListItem(item[0].title(),item[3], item[1].split(', ')[1]) for item in new_names]
	    select = dialog.select('[COLOR fffea800]'+sec.title()+'[/COLOR]', chanList, useDetails=True)
	    if not select < 0:
	        rename = True
	        remove = False
	        old_label = chanList[select].getLabel()
	        
	        original = new_names[select][2]
	        if not nameini.has_section(sec): 
	            nameini.add_section(sec)
	        if nameini.has_option(sec, original):
	            yespressed = dialog.yesno("iVue","Do you wish to delete your previous name change, or would you like to rename again", nolabel='Rename', yeslabel='Delete')
	            if yespressed:
	                rename = False
	                nameini.remove_option(sec, original)
	            else:
	                remove = True
	        if rename == True:
	            new_label = dialog.input('Enter new label', old_label, type=xbmcgui.INPUT_ALPHANUM)
	            if new_label and new_label != '':
	                if remove == True:
	                    nameini.remove_option(sec, original)
	                if not new_label == original:
	                    nameini.set(sec,original,new_label) 
	        try:namefile = open(nameFile, 'w+', encoding='utf8')
	        except:namefile = open(nameFile, 'w')
	        nameini.write(namefile)
	        namefile.close()
	        rename_chan(sec)
	    else:
	        user_menu(rename=True)
	
	
############### CHANNELS ####################
 
def showChan(sec):
	channels = []
	if channelini.has_section(sec):
		mylist = channelini.options(sec)
	else:
		mylist = []
	
	chanLists = defaultini.items(sec)
	chanLis = [item[0].title() for item in chanLists]
	chanList = []
	for listitem in chanLists:
		lis = xbmcgui.ListItem(listitem[0].title())
		lis.setArt({'icon': listitem[1].split(', ')[1]})
		chanList.append(lis)
	#chanList = [xbmcgui.ListItem(item[0].title(),'', item[1].split(', ')[1]) for item in chanLists]
	preset = [chanLis.index(item) for item in mylist if item in chanLis]
	select = dialog.multiselect('[COLOR fffea800]'+sec.title()+'[/COLOR]', chanList, preselect=preset, useDetails=True)
	
	if select:
		for chan in select:
			selected = chanLists[chan]
			channels.append(selected)
			
		if channelini.has_section(sec):
			for item in channelini.items(sec):
				channelini.remove_option(sec, item[0])
			for channel in channels:
				channelini.set(sec,channel[0].title(),channel[1]) 
			
		else:
			channelini.add_section(sec)
			for channel in channels:
				channelini.set(sec,channel[0].title(),channel[1])
				
		try:myfile = open(myFile, 'w+', encoding='utf8')
		except:myfile = open(myFile, 'w')
		channelini.write(myfile)
		myfile.close()
		channel_menu()
		
	else:
		channel_menu()
		
		
############### US/CAN LISTINGS ####################

def us_ca_listsings(name,id,country):
    if country == 'us channels':
        timeoffset = addonid.getSetting('usoffset')
    else:
        timeoffset = addonid.getSetting('canoffset')
	
    timeoffset = timeoffset.replace(':','')
    count = 0
	
    programs = []
    queuelists = []
    progdays = []
    urls = []

    for d in range(0, int(addonid.getSetting('limit'))):
        Day = dtdeep.now() + datetime.timedelta(days=d)
        get_date = Day.strftime("%Y-%m-%d")  
        urls.append(id.split(', ')[0]+'/'+get_date)

    resp = fetch_parallel(urls)
    pages = [resp.get() for _ in range(resp.qsize())]
    soup = BeautifulSoup('\n'.join(pages), "html.parser")
    found = soup.find_all("div", class_="list-group-item")
    for x in found:

        try:when = x.attrs["data-st"]
        except:when = ''
        try:title = str(x.find('a').contents[0])
        except:title = ''
        if not title =='':
            try:desc = str(x.attrs["data-description"])
            except:desc = ''
        else:
            try:title = str(x.find('span', class_="teams").contents[0])
            except:title = ''
            try:desc = str(x.find_all('p')[1].contents[0])
            except:desc = ''
        try:duration = str(x.attrs["data-duration"])
        except:duration = ''
        try:rating = str(x.attrs["data-rating"])
        except:rating = ''
        try:category = str(x.attrs["data-showtype"])
        except:category = ''

        if len(title.split())< 4:
            try:title = str(x.attrs["data-showtitle"])
            except:title = ''
        if title.endswith('- '): title = title[:-2]
        queuelists.append([when,duration,desc,rating,name,title,category])
        count +=1
    queuelists = sorted(queuelists, key=lambda x: x[0])

    for a in queuelists:
        try:
            itemnum = queuelists.index(a)
            item_num = queuelists[itemnum+1]
            next = item_num[0]
            if next == a[0]:
                item_num2 = queuelists[itemnum+2]
                next = item_num2[0]
            starttime = datetime_fix(a[0], '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
            endtime = datetime_fix(next, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
            programs.append('\t<programme start="%s %s" stop="%s %s" channel="%s">\n' % (starttime,timeoffset,endtime, timeoffset, _escape_attrib(a[4], 'utf-8')))
            programs.append('\t\t<title lang="en">%s</title>\n' % _escape_text(a[5], 'utf-8'))
            programs.append('\t\t<desc lang="en">%s</desc>\n' % _escape_text(a[2], 'utf-8'))
            programs.append('\t\t<category lang="en">5</category>\n')
            programs.append('\t\t<rating system="US">\n')
            programs.append('\t\t\t<value>%s</value>\n' % (_escape_text(a[3], 'utf-8')))
            programs.append('\t\t</rating>\n')
            programs.append('\t</programme>\n')
        except:
             pass
    if count > 0:    
        return programs
    else:
        return name
		
		
############### uk XML ####################

def uk_listsings(name, id):
    timeoffset = addonid.getSetting('ukoffset').replace(':','')
    count = 0
    programs = []
    queues = []
    Day = dtdeep.now() + datetime.timedelta(days=int(addonid.getSetting('limit'))-1)
    get_date = Day.strftime("%a %d %b")  
    get_date = datetime_fix(get_date, '%a %d %b')
	
    url = id.split(', ')[0]
    session = requests.Session()
    r = session.get(id.split(', ')[0])
    soup = BeautifulSoup(r.text, "html.parser")
    rolling_date = soup.find_all('h2')

    for x in soup.select('table'):
        xdate = rolling_date[0].text
        rolling_date.pop(0)
        current_day = datetime_fix(xdate, '%a %d %b')
        if current_day <= get_date:
	        for tr in x.select('tr'):
		        if not tr.script:
		            for td in tr.find_all('td'):
	
		                a = ''.join(re.sub(r'\s+', ' ', td.text))
		                b = a.strip()
	
		                if b[:1] in '0123456789':
		                    time = b
		                else:
		                    try:title = td.find_all("div", class_="title")[0].text.strip()
		                    except:title = ''
		                    if ' Rating' in b:
		                        c = b.split(' Rating')
		                    else:
		                        c = b.split(' Rating')
		                        c.append(0.0)
		
		                    desc = c[0]
		                    queues.append([xdate,time,desc,str(c[1]).replace(': ',''),name,title.replace('?','')])
		                    count += 1

    now = dtdeep.now()
    laststart = now - datetime.timedelta(days=1)
    lastend = now - datetime.timedelta(days=1)
	
    for a in queues:
        item_num = queues.index(a)
        try:
	        next = queues[item_num+1]
	        starttime = datetime_fix(' '.join([str(now.year), a[0], a[1]]), '%Y %a %d %b %I:%M%p')
	        endtime = datetime_fix(' '.join([str(now.year), next[0], next[1]]), '%Y %a %d %b %I:%M%p')
		
	        while starttime < laststart:
	            starttime = starttime + datetime.timedelta(days=1)
	        while endtime < lastend:
	            endtime = endtime + datetime.timedelta(days=1)
		    
	        laststart = starttime
	        lastend = endtime
	        starttime = starttime.strftime('%Y%m%d%H%M%S')
	        endtime = endtime.strftime('%Y%m%d%H%M%S')
		
	        programs.append('\t<programme start="%s %s" stop="%s %s" channel="%s">\n' % (starttime,timeoffset,endtime,timeoffset, _escape_attrib(a[4], 'utf-8')))
	        programs.append('\t\t<title lang="en">%s</title>\n' % _escape_text(a[5], 'utf-8'))
	        programs.append('\t\t<desc lang="en">%s</desc>\n' % _escape_text(a[2], 'utf-8'))
	        programs.append('\t\t<category lang="en">5</category>\n')
	        programs.append('\t\t<rating system="UK">\n')
	        programs.append('\t\t\t<value>%s</value>\n' % _escape_text(a[3], 'utf-8'))
	        programs.append('\t\t</rating>\n')
	        programs.append('\t</programme>\n')
        except:
	        pass
    if count > 0:
        return programs
    else:
        return name
	
	
############### AUS LISTINGS ####################

def aus_listsings(name,id):
    timeoffset = addonid.getSetting('ausoffset')
    timeoffset = timeoffset.replace(':','')
    count = 0
	
    programs = []
    queuelists = []
    progdays = []
    urls = []

    for d in range(0, int(addonid.getSetting('limit'))):
        Day = austime() + datetime.timedelta(days=d)
        get_date = Day.strftime("%Y-%m-%d")  
        #urls.append(id.split(', ')[0]+'?dt='+get_date)
        session = requests.Session()
        r = session.get(id.split(', ')[0]+'?dt='+get_date)
        #resp = fetch_parallel(urls)
        #pages = [resp.get() for _ in range(resp.qsize())]
        #content = '\n'.join(pages)
        soup = BeautifulSoup(r.text, "html.parser")
        for x in soup.select('table'):
            for tr in x.select('tr'):
	            if not tr.script:
	                for td in tr.find_all('td'):
	                    ttime = td.find_all("h5", class_="thin")[0].text
	                    if ttime[:1] in '0123456789':
	                        time = ttime
	                    else:
	                        title = td.find('a').text.strip()
	                        try:desc = td.find('h6').text.strip()
	                        except:desc = 'No Information available'
	                        queuelists.append([time,title,desc,name,get_date])
	                        count += 1

    now = austime()
    laststart = now - datetime.timedelta(days=1)
    lastend = now - datetime.timedelta(days=1)
	
    for a in queuelists:
        item_num = queuelists.index(a)
        try:
	        next = queuelists[item_num+1]
	        starttime = datetime_fix(' '.join([a[4], a[0]]), '%Y-%m-%d %I:%M %p')
	        endtime = datetime_fix(' '.join([next[4],  next[0]]), '%Y-%m-%d %I:%M %p')
		
	        while starttime < laststart:
	            starttime = starttime + datetime.timedelta(days=1)
	        while endtime < lastend:
	            endtime = endtime + datetime.timedelta(days=1)
		    
	        laststart = starttime
	        lastend = endtime
	        starttime = starttime.strftime('%Y%m%d%H%M%S')
	        endtime = endtime.strftime('%Y%m%d%H%M%S')
		
	        programs.append('\t<programme start="%s %s" stop="%s %s" channel="%s">\n' % (starttime,timeoffset,endtime,timeoffset, _escape_attrib(a[3], 'utf-8')))
	        programs.append('\t\t<title lang="en">%s</title>\n' % _escape_text(a[1], 'utf-8'))
	        programs.append('\t\t<desc lang="en">%s</desc>\n' % _escape_text(a[2], 'utf-8'))
	        programs.append('\t\t<category lang="en">5</category>\n')
	        programs.append('\t\t<rating system="AUS">\n')
	        programs.append('\t\t\t<value>0</value>\n')
	        programs.append('\t\t</rating>\n')
	        programs.append('\t</programme>\n')
        except:
	        pass
    if count > 0:
        return programs
    else:
        return name
        
        
############### MAKE XML ####################

def xml_config(xml=None):
	days ='day'
	limit = int(addonid.getSetting('limit'))
	if limit > 1: days+= 's'
	dp = xbmcgui.DialogProgress()
	dp.create('Grabbing EPG', "Please Wait")
	channels = channelini.sections()
	total = 0
	for item in channels:
	    for count in channelini.items(item):
	        total +=1
	if total == 0:
	    dialog.ok('iVue', 'No channales found. Please select what channels you want in ivue settings')
	    return 'Fetch Failed'
	errors = []
	grabcount = 0
	passed = -1
	if xml == None:
	    try:xml = open(userxml, 'w+', encoding='utf8')
	    except:xml = open(userxml, 'w+')
	scraped = []
	xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	xml.write('<tv>\n')
	
	try:

		for chan in channels:
		    for name, id in channelini.items(chan):
			    passed += 1
			    per = 100.0 / total * passed
			    if dp.iscanceled():
				    xml.close()
				    try:os.remove(userxml)
				    except: pass
				    return 'Fetch Failed'
			    try: 
				    dp.update(int(per), '[COLOR orange]Grabbing '+str(limit)+' '+days+' listings for: [/COLOR]'+name+ '\n[COLOR orange]Channels: [/COLOR]'+str(passed)+' / '+str(total)+'\n[COLOR orange]Errors: [/COLOR]'+str(len(errors))+'\n')
				    if nameini.has_option(chan, name):
				        name = nameini.get(chan, name)
				    if chan == 'uk channels':
				        grabbed = uk_listsings(name,id)
				    elif chan == 'australia channels':
				        grabbed = aus_listsings(name,id)
				    else:
				        grabbed = us_ca_listsings(name,id,str(chan))
				
				    if not grabbed == name:
				        grabcount += 1
				        scraped.append(grabbed)
				        xml.write('\t<channel id="%s">\n' % _escape_attrib(name, 'utf-8'))
				        xml.write('\t\t<display-name lang="en">%s</display-name>\n' % _escape_text(name, 'utf-8'))
				        xml.write('\t\t<icon src="%s" />\n' % _escape_attrib(id.split(', ')[1], 'utf-8'))
				        xml.write('\t\t<url>iVue EPG Grabber</url>\n')
				        xml.write('\t</channel>\n')
				    else:
				        errors.append(name)
				    
			    except Exception as e:
				    errors.append(name)
	except Exception as e:
		grabcount = 0
			
	scraped = sum(scraped,[])
	try:xml.write(''.join(scraped))
	except:xml.write(''.join(scraped).replace('&', '&amp;')) 
	xml.write('</tv>')
	try:dp.close()
	except:pass
	xml.close()
	if len(errors) > 0 and grabcount > 0:
	    dialog.ok('Errors with channels', 'The following channels have been removed: ' +', '.join(errors))
	if grabcount > 0:
	    return 'Fetch OK'
	else:
	    dialog.ok('iVue', 'Problem making xml please check your internet. If your connection is ok there maybe a problem with iVue XML Grab. Please try again, if problem occurs contact team iVue')
	    try:os.remove(userxml)
	    except:pass
	    return 'Fetch Failed'
	

############### CATS ####################

def cat_menu():
	sections = currentcatini().sections()
	options = ['Add New Category'] + sections
	select = dialog.select('[COLOR fffea800]iVue Channel Menu[/COLOR]', options)
	if not select < 0:
	    if select == 0:
		
		    new_label = dialog.input('Enter new label','', type=xbmcgui.INPUT_ALPHANUM)
		    if new_label and new_label != '':
		        if not currentcatini().has_section(new_label):
		            currentcatini().add_section(new_label)
		            try:myfile = open(currentCats, 'w+', encoding='utf8')
		            except:myfile = open(currentCats, 'w')
		            currentcatini().write(myfile)
		            myfile.close()
		            cat_menu()
	    else:
		    sec = options[select]
		    catoptions = currentcatini().options(sec)
		    cat_channels(sec, catoptions)
		
def addcat_chan(sec, catoptions):
	try:
	    created = currentcatini().sections()
	    channelList = currentChannels(catoptions, new=True)
	    options = []
	    channelList = sorted(channelList, key=lambda s: s[0])
	    
	    for line in channelList:
	        cats = []
	        for saved in created:
	            if line[0] in currentcatini().options(saved):
	                cats.append(saved)
	        lis = xbmcgui.ListItem(line[0],', '.join(cats))
	        lis.setArt({'icon': line[1]})
	        options.append(lis)
	    select = dialog.multiselect('[COLOR fffea800]'+sec+'[/COLOR]', options, useDetails=True)
	    if not select:
	        cat_channels(sec,catoptions)
	    elif select:
	        for chan in select:
	            selected = channelList[chan][0]
	            currentcatini().set(sec,selected,sec)
	        try:myfile = open(currentCats, 'w+', encoding='utf8')
	        except:myfile = open(currentCats, 'w')
	        currentcatini().write(myfile)
	        myfile.close()
	        cat_channels(sec,catoptions)
	except: 
	    dialog.ok('iVue', 'No channels found. Please run iVue first so we can get your channel list')
	    cat_menu()
	
def cat_channels(sec, opt):
    newlis = xbmcgui.ListItem('Add New Channels')
    newlis.setArt({'icon': chanlogo})
    options=[newlis]
    myList = currentChannels(opt, new=False)
    myList = sorted(myList, key=lambda s: s[0])
    for item in myList:
        lis = xbmcgui.ListItem(item[0])
        lis.setArt({'icon': item[1]})
        options.append(lis)

    #options.insert(0, xbmcgui.ListItem('Add New Channels','', chanlogo))

    select = dialog.select('[COLOR fffea800]'+sec+' Menu[/COLOR]', options, useDetails=True)
    if not select < 0:
        if select == 0:
            addcat_chan(sec, opt)
        else:
            channel = options[select].getLabel()
            yespressed = dialog.yesno("iVue","Do you wish to remove "+channel+ " from your "+ sec+" category", nolabel='Cancel', yeslabel='Remove')
            if yespressed:
                currentcatini().remove_option(sec, channel)
                try:myfile = open(currentCats, 'w+', encoding='utf8')
                except:myfile = open(currentCats, 'w')
                currentcatini().write(myfile)
                myfile.close()
                cat_channels(sec, opt)
            else:
                cat_channels(sec, opt)
    else:
        cat_menu()
	
def currentChannels(sec, new):
	channelList = []
	databasePath = os.path.join(userpath, 'master.db')
	conn = sqlite3.connect(databasePath, detect_types=sqlite3.PARSE_DECLTYPES)    	
	c = conn.cursor()
	c.execute('SELECT * FROM channels WHERE source=? AND visible=? ORDER BY weight', ["xmltv", True])
	for row in c:
	    if new == True:
	        if not row[1] in sec:
	            channelList.append([row[1], row[2]])
	    else:
	        if row[1]in sec:
	            channelList.append([row[1], row[2]])
	c.close()
	return channelList
############### FORMATTING ####################

_escape_map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
}


if sys.version[:3] == "1.5":
    _escape = re.compile(r"[&<>\"\x80-\xff]+")
else:
    _escape = re.compile(eval(r'u"[&<>\"\u0080-\uffff]+"'))


def _encode(s, encoding):
    try:
        if pyver >= 3: return s.encode(encoding).decode('utf-8', 'ignore')
        else: return s.encode(encoding)
    except AttributeError:
        return s
        
        
def _encode_entity(text, pattern=_escape):
	
    def escape_entities(m, map=_escape_map):
        out = []
        append = out.append
        
        for char in m.group():
            text = map.get(char)
            if text is None:
                text = "&#%d;" % ord(char)
            append(text)
            
        return ''.join(out, "")
        
    try:
        return _encode(pattern.sub(escape_entities, text), "ascii")
    except TypeError:
        return text
        
        
def _escape_text(text, encoding=None):
    try:
        if encoding:
            try:
                text = _encode(text, encoding)
            except UnicodeError:
                return _encode_entity(text)
        text = text.replace( "&", "&amp;")
        text = text.replace( "<", "&lt;")
        text = text.replace( ">", "&gt;")
        if pyver >= 3:
            return text.decode('utf-8', 'ignore').replace('&', '&amp;')
        else:
            return text
    except (TypeError, AttributeError):
        return text
        

def _escape_attrib(text, encoding=None):
    try:
        if encoding:
            try:
                text = _encode(text, encoding)
            except UnicodeError:
                return _encode_entity(text)
        text = text.replace( "&", "&amp;")
        text = text.replace( "'", "&apos;")
        text = text.replace( "\"", "&quot;")
        text = text.replace( "<", "&lt;")
        text = text.replace( ">", "&gt;")
        if pyver >= 3:
            return text.decode('utf-8', 'ignore').replace('&', '&amp;')
        else:
            return text
    except (TypeError, AttributeError):
        return text
      
  
def datetime_fix(string_date, format):
    try:
        fix = dtdeep.strptime(string_date, format)
    except TypeError:
        fix = dtdeep(*(time.strptime(string_date, format)[0:6]))
    return fix


def austime():
    os.environ['TZ']='Australia/Adelaide'
    austime = dtdeep.now()
    os.environ.clear()
    return austime


################ THREADS AND QUEUES #################
def read_url(url, queue):
    session = requests.Session()
    data = session.get(url).text
    queue.put(data)

def fetch_parallel(urls_to_load):
    result = Queue.Queue()
    threads = [threading.Thread(target=read_url, args = (url,result)) for url in urls_to_load]
    for t in threads:
        t.daemon = True
        t.start()
    for t in threads:
        t.join()
    return result
	
def lock_parallel(urls_to_load):
    result = Queue.Queue()
    lock = threading.Lock()
    with lock:
        threads = [threading.Thread(target=read_url, args = (url,result)) for url in urls_to_load]
        for t in threads:
            t.daemon = True
            t.start()
        for t in threads:
            t.join()
    return result

if prnum == 'main':
    channel_menu()
    
if prnum == 'cats':
    cat_menu()
    
elif prnum == 'rename':
    user_menu(rename=True, chans=False, names=False)
    
elif prnum == 'removechan':
    user_menu(rename=False, chans=True,names=False)
    
elif prnum == 'removenames':
    user_menu(rename=False, chans=False, names=True)
 
elif prnum == 'grab':
    try:file = open(userxml, 'w+', encoding='utf8')
    except:file = open(userxml, 'w')
    xml_config(file)

