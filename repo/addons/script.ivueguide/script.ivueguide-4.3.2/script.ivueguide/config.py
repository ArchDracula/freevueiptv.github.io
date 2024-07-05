import xbmc, xbmcgui, shutil, os, xbmcaddon, zipfile, time, re, base64, sys
try:import urllib.request as urlrequest
except:import urllib2 as urlrequest
try:import urllib
except:pass
from os import _exit as pageConfig
import shutil
import utils
import xbmcvfs
from sqlite3 import dbapi2 as database
try: translatePath = xbmcvfs.translatePath
except: translatePath = xbmc.translatePath

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
    text_type = str
    binary_type = bytes
else:
    string_types = basestring,
    text_type = unicode
    binary_type = str
    
def ensure_str(s, encoding='utf-8', errors='strict'):

    if not isinstance(s, (text_type, binary_type)):
        raise TypeError("not expecting type '%s'" % type(s))
    if PY2 and isinstance(s, text_type):
        s = s.encode(encoding, errors)
    elif PY3 and isinstance(s, binary_type):
        s = s.decode(encoding, errors)
    return s

addon_id = 'script.FreeVueGuide'
addon_name = xbmcaddon.Addon(addon_id)
pageNum = addon_name.getAddonInfo('Path')
currentKodi = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
HOME = addon_name.getAddonInfo('path')
ICON = os.path.join(HOME, 'icon.png')
PACKAGES       = translatePath(os.path.join('special://home'))
TEMP =	  addon_name.getSetting('tempskin')
USER_AGENT     = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
#Karls changes

ivue = utils.folder()
d = xbmcgui.Dialog()
dp = xbmcgui.DialogProgress()
skin = addon_name.getSetting('skin')
path = translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins'))
Skinxml = translatePath(os.path.join(path, skin, '720p', 'script-tvguide-main.xml'))
xmlData = translatePath('special://profile/addon_data/script.FreeVueGuide/resources/config/Data.txt')
logoData = translatePath('special://profile/addon_data/script.FreeVueGuide/resources/config/Logo.txt')
catData = translatePath('special://profile/addon_data/script.FreeVueGuide/resources/categories/')	
kodiskin = translatePath('special://skin/')
skinfontfolder = translatePath('special://skin/fonts')
databasePath = translatePath('special://profile/Database')
addons27 = os.path.join(databasePath, 'Addons27.db')
ivue = ensure_str(utils.folder())
players = base64.b64decode('aHR0cDovL,2l2dWV0dmd1aWRlLmNv,bS9pdnVlZ3VpZGV4bWwvc.=mFkaW8vdGltZXMudHh0')
FOAlist = ''
proglist = []



prnum=""
try:
    prnum= sys.argv[ 1 ]
except:
    pass
    
    


def openURL(url):
	  req = urlrequest.Request(url)
	  req.add_header('User-Agent', USER_AGENT)
	  response = urlrequest.urlopen(req)
	  link=response.read()
	  link = ensure_str(link)
	  response.close()
	  return link
	
def retrieve(url,zipfile,dp):
    try:urlrequest.urlretrieve(url,zipfile,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
    except:urllib.urlretrieve(url,zipfile,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
    return url

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
	try:
		percent = min((numblocks*blocksize*100)/filesize, 100)
		dp.update(int(percent))
	except:
		percent = 100
		dp.update(percent)
	if dp.iscanceled():
		raise Exception("Cancelled")
		dp.close()
		
def radio(play, path):
    for item in proglist:
        try:
            if item.split(' =')[0] == str(play):
                location = str(path).split('url=')[1].split('%3A80')[0]
                if item.split('= ')[1] == location :
                    return True
                else:
                    return False
        except:
            if item == str(play):
                return False
            else:
                return True


def listskins():
    files = [] 
    if os.path.exists(path):
        for name in os.listdir(path): 
            files.append(name)
        skin = d.select("ivue", files)
        if skin == -1:
            return
        else:
            selected = files[skin]            
            resetSkinSet(selected)
    else:
        d.ok('Ivue', 'Skin Folder Missing Please run iVue to complete setup')

def getskins():
    folder = ivue+'/skins/'
    view = openURL(folder)
    match=re.compile('<a href="(.*?)">').findall(view)
    notneeded = ['/ivueguide/', 'index.htmlofflineforabit', '/ivueguide//','/ivueguidexml//', 'skins.zip']
    files = [] 
    for name in match:
        if not name.startswith('?') and name not in notneeded:
            name = re.sub(r'%20', ' ', name)
            name = re.sub(r'.zip', '', name)
            if not name in os.listdir(path):
                files.append(name)
    skin = d.select("ivue", files)
    if skin == -1:
        return
    else:
        selected = files[skin]
        zipurl = ivue+'/skins/%s.zip' % (selected).replace(' ', '%20') 
        zipfile = os.path.join(PACKAGES,"%s.zip" % selected) 
        dp.create("iVue","Downloading %s" % selected)
        retrieve(zipurl,zipfile,dp)
        try:shutil.unpack_archive(zipfile, path)
        except:xbmc.executebuiltin("XBMC.Extract(%s, %s)" % ( zipfile.encode("utf-8"), path.encode("utf-8")), True)
        time.sleep(1)
        dp.close() 
        if os.path.exists(path + "/%s" % selected):
        	resetSkinSet(selected, file=zipfile)
        else:
            d.ok('Ivue', 'Download failed Please try downloading again')
 
def delskins():
    files = [] 
    if os.path.exists(path):
        for name in os.listdir(path): 
            files.append(name)
        skin = d.select("ivue", files)
        if skin == -1:
            return
        else:
            selected = files[skin]
            installed = translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', '%s' % selected))
            shutil.rmtree(installed)
            if not os.path.exists(installed):
                d.ok("iVue", '%s has been successfully removed' % selected)
            else:
                d.ok("iVue", '%s was not removed' % selected)
    else:
        d.ok('Ivue', 'No skins installed Please run iVue to complete setup')

def resetSkinSet(selected, file=None):
	if selected == 'Christmas':
		addon_name.setSetting('last.skin', addon_name.getSetting('skin'))
	addon_name.setSetting('download.skin', '')
	if addon_name.getSetting('scroll.chan') == 'Disabled':
		scrollText(scrolling=1)
		addon_name.setSetting('scroll.chan', 'Enabled')
	if addon_name.getSetting('Font') == 'Enabled':
		fontSize(font=1)
		addon_name.setSetting('font', 'Disabled')
	addon_name.setSetting('skin', '%s' % selected)
	
	if not file == None:
		os.remove(file)
		
	if os.path.exists(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', selected, 'fonts'))):
		xbmc.executebuiltin('SendClick(10140,28)')
		d.ok("iVue", selected+' now has its own fonts you can use within iVue. Skin fonts will help with text alignment, visual impaired setting and also keeping the original look to the skin')
		yes_pressed = d.yesno('[COLOR ffff7e14][B]IVUE FONTS[/B][/COLOR]', 'Do you wish to use ivue fonts or keep kodi default',nolabel='Kodi',yeslabel='iVue')
		if yes_pressed:
			setfont(type=selected)
		else:
			resetfont(type=selected)


def page(pageid):
    return os.stat(pageNum+"/"+base64.b64decode(pageid).decode('utf-8')).st_size


def updater():
	message = 'Checking addon Updates'
	xbmc.executebuiltin('XBMC.Notification(%s, %s, '', %s)' % (addon_id, message, ICON))
	xbmc.executebuiltin("XBMC.UpdateaddonRepos()")
	d.ok("iVue", 'CHECKING FOR REPO UPDATES SUCCESSFUL :) [COLOR gold]Brought To You By iVue[/COLOR]')
	return

def enableRepo():
    try:
        getDB = database.connect(addons27)
        getDB.execute('update installed set enabled=1 WHERE addonID = ?', ['xbmc.repo.FreeVueGuide'])
        getDB.commit()
    except:
        pass
    xbmc.executebuiltin("XBMC.UpdateLocalAddons()")
    time.sleep(1)
    xbmc.executebuiltin("XBMC.UpdateaddonRepos()")
    xbmc.executebuiltin('XBMC.Notification(%s, Enabling iVue repo, '', %s)' % (addon_id, ICON))
	
def setXmlUrl():
    if os.path.exists(xmlData):
        xml = open(xmlData,'rb').read()
        xml = ensure_str(xml)
        matches = re.compile('name="(.*?)".+?url="(.*?)"').findall(xml)
        subbedaddons = {}
            
        for name, value in matches:
            subbedaddons[name] = value
			
        names = sorted(subbedaddons)
 
        selection = d.select('[COLOR fffea800]Xmls[/COLOR]', names)
        if selection < 0:
            return
        else:
            sub_name = names[selection]
            link = subbedaddons[sub_name]
            addon_name.setSetting('sub.xmltv', sub_name)
            addon_name.setSetting('sub.xmltv.url', link)
            try:
                check_files = sub_name.split(' (')[0]
            except:
                check_files = sub_name

            if os.path.exists(os.path.join(catData,check_files+'.ini')) and not addon_name.getSetting('categories.path') == check_files:
                yes_pressed = d.yesno('[COLOR ffff7e14][B]IVUE SETUP[/B][/COLOR]', 'Do you wish to use ' +check_files+ ' categories',nolabel='no',yeslabel='yes')
                if yes_pressed:
                    addon_name.setSetting('categories.path', check_files)
            if (os.path.exists(logoData) and not addon_name.getSetting('sub.logos') == check_files) or (os.path.exists(logoData) and not int(addon_name.getSetting('logos.source')) == 1):
                logos = open(logoData).read()
                matches = re.compile('name="(.*?)".+?logo="(.*?)"').findall(logos)
            
                for name, value in matches:
                    if name == check_files:
                        yes_pressed = d.yesno('[COLOR ffff7e14][B]IVUE SETUP[/B][/COLOR]', 'Do you wish to use ' +check_files+ ' logo pack',nolabel='no',yeslabel='yes')
                        if yes_pressed:
                            addon_name.setSetting('logos.source', '1')
                            addon_name.setSetting('sub.logos', check_files)
                            addon_name.setSetting('sub.logos.url', value)
            d.ok('iVue', 'Please press ok in settings dialog to confirm changes, then reload guide for changes to take affect')

		
def setlogoUrl():
    if os.path.exists(logoData):
        logos = open(logoData,'rb').read()
        logos = ensure_str(logos)
        matches = re.compile('name="(.*?)".+?logo="(.*?)"').findall(logos)
        subbedaddons = {}
            
        for name, value in matches:
            subbedaddons[name] = value
			
        names = sorted(subbedaddons)
 
        selection = d.select('[COLOR fffea800]Logo Packs[/COLOR]', names)
        if selection < 0:
            return
        else:
            sub_name = names[selection]
            link = subbedaddons[sub_name]
            addon_name.setSetting('sub.logos', sub_name)
            addon_name.setSetting('sub.logos.url', link)




def setcat():
    subbedaddons = []
    if os.path.exists(catData):
	
        for file in os.listdir(catData):
            subbedaddons.append(file.replace('.ini', ''))
			
        names = sorted(subbedaddons)
 
        selection = d.select('[COLOR fffea800]Categories file[/COLOR]', names)
        if selection < 0:
            return
        else:
            sub_name = names[selection]
            addon_name.setSetting('categories.path', sub_name)
            xbmc.executebuiltin('SendClick(%s)' % utils.fixSettings(query='0.0', get_button=True))

            utils.fixSettings(query='1.1')

def resetfont(type):
	findFolder = utils.xbmcvfs.File(os.path.join(kodiskin, 'addon.xml'),'rb').read()
	findFolder = ensure_str(findFolder)
	match = re.compile('folder="(.*?)"').findall(findFolder)
	folder = match[0]
	if os.path.exists(os.path.join(kodiskin, folder, 'originalFont.xml')):
	    shutil.copy(os.path.join(kodiskin, folder, 'originalFont.xml'),os.path.join(kodiskin, folder, 'Font.xml'))
	if os.path.exists(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p_original'))):
	    shutil.rmtree(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p')))
	    os.rename(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p_original')),translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p')))
	xbmc.executebuiltin("XBMC.ReloadSkin()")

def setfont(type):

	findFolder = utils.xbmcvfs.File(os.path.join(kodiskin, 'addon.xml'),'rb').read()
	findFolder = ensure_str(findFolder)
	match = re.compile('folder="(.*?)"').findall(findFolder)
	folder = match[0]
	if not os.path.exists(os.path.join(kodiskin, folder, 'originalFont.xml')):
	    shutil.copy(os.path.join(kodiskin, folder, 'Font.xml'),os.path.join(kodiskin, folder, 'originalFont.xml'))
	
	
	skinfont = translatePath(os.path.join(kodiskin, folder, 'originalFont.xml'))
	
	if str(folder) == '720p':
		fontres = translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, 'fonts', 'files', 'ivuefont720.txt'))
		f1 = open(fontres, 'rb')
	else:
		fontres = translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, 'fonts', 'files', 'ivuefont.txt'))
		f1 = open(fontres, 'rb')
	f = open(skinfont, 'rb')
	try: f2 = open(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, 'fonts', 'files', 'Font.xml')), 'w', encoding='utf-8')
	except: f2 = open(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, 'fonts', 'files', 'Font.xml')), 'w')
	
	f2.write('<!-- Added iVue Fonts -->\n')
	for line in f.readlines():
		line = ensure_str(line)
		f2.write(line)
		if 'fontset id' in line:
			f1 = open(fontres, 'rb')
			f2.write('\n')
			for newline in f1.readlines():
				newline = ensure_str(newline)
				f2.write(newline)
			f2.write('\n')
			f1.close()
			
	f1.close()
	f2.close()
	f.close()
	shutil.move(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, 'fonts', 'files', 'Font.xml')), os.path.join(kodiskin, folder, 'Font.xml'))
	font_files = os.listdir(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, 'fonts')))
	for file_name in font_files:
	    full_file_name = translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, 'fonts', file_name))
	    if os.path.isfile(full_file_name):
	        shutil.copy(full_file_name, os.path.join(skinfontfolder, file_name))
	if not os.path.exists(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p_original'))):
	    os.rename(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p')),translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p_original')))
	try:
		shutil.rmtree(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p')))
	except:
		pass
	shutil.copytree(translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, 'fonts', 'files', '720p')), translatePath(os.path.join('special://profile', 'addon_data', 'script.FreeVueGuide', 'resources', 'skins', type, '720p')))
	xbmc.executebuiltin("XBMC.ReloadSkin()")


def scrollText(scrolling=None):
    if scrolling == None:
        scrolling = d.select("ivue", ['Disable scrolling', 'Enable scrolling'])
    if scrolling == 0:
        if os.path.exists(Skinxml):
            f1=open(Skinxml,'rb').read()
            f1 = ensure_str(f1)
            if '<scroll' in f1:
                try:f2=open(Skinxml,'w', encoding='utf-8') 
                except:f2=open(Skinxml,'w')
                m=f1.replace('scroll','nonscroll')
                f2.write(m) 
                f2.close()
            addon_name.setSetting('scroll.chan', 'Disabled')

    if scrolling == 1:

        if os.path.exists(Skinxml):
            f1=open(Skinxml,'rb').read()
            f1 = ensure_str(f1)
            if '<nonscroll' in f1:
                try:f2=open(Skinxml,'w', encoding='utf-8') 
                except:f2=open(Skinxml,'w')
                m=f1.replace('nonscroll','scroll')
                f2.write(m)   
                f2.close()
            addon_name.setSetting('scroll.chan', 'Enabled')
    else:
        return

def fontSize(font=None):
    if font == None:
        font = d.select("ivue", ['Enable large font', 'Disable large font'])
    if font == 0:
        if os.path.exists(Skinxml):
            f1=open(Skinxml,'rb').read()
            f1 = ensure_str(f1)
            if 'font' in f1:   
                try:f2=open(Skinxml,'w', encoding='utf-8') 
                except:f2=open(Skinxml,'w')
                m=f1.replace('font13','font30').replace('font12', 'font16')
                f2.write(m)    
                f2.close()
            addon_name.setSetting('font', 'Enabled')

    elif font == 1:

        if os.path.exists(Skinxml):
            f1=open(Skinxml,'rb').read()
            f1 = ensure_str(f1)
            if 'font' in f1:
                try:f2=open(Skinxml,'w', encoding='utf-8') 
                except:f2=open(Skinxml,'w')
                m=f1.replace('font30','font13').replace('font16', 'font12')
                f2.write(m)    
                f2.close()
            addon_name.setSetting('font', 'Disabled')
    else:
        return




 


if prnum == 'Custom':
    Custom()
 
elif prnum == 'List':
    listskins() #setfont() 


elif prnum == 'Get':
    getskins()


elif prnum == 'Delete':
    delskins()

elif prnum == 'Update':
    updater()
	
elif prnum == 'setxml':
    setXmlUrl()
	
elif prnum == 'logo':
    setlogoUrl()

elif prnum == 'setcat':
    setcat()

elif prnum == 'scroll':
    scrollText()

elif prnum == 'font':
    fontSize()


