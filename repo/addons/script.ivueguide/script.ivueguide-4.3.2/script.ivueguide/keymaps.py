import xbmcaddon,os,time
import xbmcgui

ADDONID = 'script.FreeVueGuide'
ADDON = xbmcaddon.Addon(ADDONID) 
HOME = ADDON.getAddonInfo('path')
RESOURCES = os.path.join(HOME, 'resources')
mapkeyxml = os.path.join(HOME, RESOURCES, 'keymaps')
d = xbmcgui.Dialog()

ACTION_LEFT = 1
ACTION_RIGHT = 2
ACTION_UP = 3
ACTION_DOWN = 4
ACTION_SELECT_ITEM = 7
ACTION_PARENT_DIR = 9
ACTION_MOUSE_SELECT = 100
ACTION_MOUSE_MOVE = 107
KEY_NAV_BACK = 92

class ActionGrabber(xbmcgui.WindowXMLDialog):
    TIMEOUT = 6

    def __new__(cls, type):
        file_name = 'keymap.xml'

        return super(ActionGrabber, cls).__new__(cls, file_name, HOME, "keymaps")

    def __init__(self, type):
        self.type = type
        self.key = None

    def onAction(self, action):
        code = action.getId()
        
        if code in [ACTION_PARENT_DIR, KEY_NAV_BACK]:       
            self.key = ADDON.getSetting(self.type) 
            self.close()
            
        elif not code in [ACTION_LEFT, ACTION_RIGHT, ACTION_UP, ACTION_DOWN, ACTION_SELECT_ITEM, ACTION_MOUSE_SELECT, ACTION_MOUSE_MOVE]:
            self.key = str(code)
            self.close()

    @staticmethod
    def get_action(type):
        dialog = ActionGrabber(type)
        dialog.doModal()
        key = dialog.key
        if not key == ADDON.getSetting(type):
            d.ok('Team iVue', 'KEYMAP SUCCESSFUL, Please run iVue and check its working')
        ADDON.setSetting(type, key)
        del dialog
        
prnum=""
try:
    prnum= sys.argv[ 1 ]
except:
    pass
    
if prnum == 'Categories':
    ActionGrabber.get_action('cat_keymap')
    
elif prnum == 'Sports':
    ActionGrabber.get_action('sport_keymap')
    
    