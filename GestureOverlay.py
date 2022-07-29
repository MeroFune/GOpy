import openvr
import os
import time as time
import asyncio
import json

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher

# Icons
PATH_NEUTRAL = os.path.join(os.path.dirname(__file__), 'Images', 'Neutral.png')
PATH_FINGERGUN = os.path.join(os.path.dirname(__file__), 'Images', 'FingerGun.png')
PATH_FIST = os.path.join(os.path.dirname(__file__), 'Images', 'Fist.png')
PATH_OPENHAND = os.path.join(os.path.dirname(__file__), 'Images', 'OpenHand.png')
PATH_POINT = os.path.join(os.path.dirname(__file__), 'Images', 'Point.png')
PATH_ROCKANDROLL = os.path.join(os.path.dirname(__file__), 'Images', 'RockAndRoll.png')
PATH_THUMBSUP = os.path.join(os.path.dirname(__file__), 'Images', 'ThumbsUp.png')
PATH_VICTORY = os.path.join(os.path.dirname(__file__), 'Images', 'Victory.png')

# update rate of the main loop, also affects transparency fade anim
UPDATE_RATE = 60 

# default settings
settings = {
    "VRC OSC IP": "127.0.0.1",
    "VRC OSC port": 9001,
    "Colour": [0, 1, 1],
    "Transparency": 0.85,
    "Normalised icon X position": 0.28,
    "Normalised icon Y position": -0.41, 
    "Icon plane depth": 0.9,
    "Normalised icon width": 0.16,
    "Fade time": 5,
    "Fade interval": 2,
    "Disable fist": 0, 
    "Disable openhand": 0, 
    "Disable point": 0, 
    "Disable victory": 0, 
    "Disable rocknroll": 0, 
    "Disable fingergun": 0, 
    "Disable thumbsup": 0
}

gestureDisableArr = [0, 0, 0, 0, 0, 0, 0, 0]

### Utilities ##################################################################
def mat34Id():
    arr = openvr.HmdMatrix34_t()
    arr[0][0] = 1
    arr[1][1] = 1
    arr[2][2] = 1
    return arr

### Classes ####################################################################

class OSCHandler:
    def __init__(self, uiMan) -> None:
        self.VRC_OSC_IP = settings['VRC OSC IP']
        self.VRC_OSC_ADDRESS = settings['VRC OSC port']

        self.uiMan = uiMan

        ## python-osc methods
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/avatar/parameters/Gesture*", self.filterHand)

    def detectRightGesture(self, id):
        if type(id) == int: # ensure we don't get the weight param instead
            print(f"GOpy: Gesture right changed to {id}")
            self.uiMan.rightHandUpdate(id)

    def detectLeftGesture(self, id):
        if type(id) == int:
            print(f"GOpy: Gesture left changed to {id}")
            self.uiMan.leftHandUpdate(id)

    def filterHand(self, address: str, arg):
        # filter the address
        if "GestureRight" in address:
            self.detectRightGesture(arg)
        elif "GestureLeft" in address:
            self.detectLeftGesture(arg)

    async def initServer(self):
        server = AsyncIOOSCUDPServer((self.VRC_OSC_IP, self.VRC_OSC_ADDRESS), 
                                      self.dispatcher, asyncio.get_event_loop())
        
        await server.create_serve_endpoint()

class UIElement:
    def __init__(self, overlayRoot, key, name, pos, flip = False) -> None:
        """
        pos is a 2-tuple representing (x, y) normalised position of the overlay on the screen
        """
        self.overlay = overlayRoot
        self.overlayKey = key
        self.overlayName = name
        self.flip = flip

        self.handle = self.overlay.createOverlay(self.overlayKey, 
                                                 self.overlayName)

        # configure overlay appearance
        self.setImage(PATH_NEUTRAL) # blank image for default
        self.setColour(settings['Colour'])
        self.setTransparency(settings['Transparency'])
        self.overlay.setOverlayWidthInMeters(self.handle, 
                                             settings['Normalised icon width'] * settings['Icon plane depth'])

        self.setPosition(pos)

        self.overlay.showOverlay(self.handle)

    def setImage(self, path):
        self.overlay.setOverlayFromFile(self.handle, path)

    def setColour(self, col):
        """
        col is a 3-tuple representing (r, g, b)
        """
        self.overlay.setOverlayColor(self.handle, col[0], col[1], col[2])
    
    def setTransparency(self, a):
        self.overlay.setOverlayAlpha(self.handle, a)

    def setPosition(self, pos):
        """
        pos is a 2-tuple representing normalised (x, y)
        """
        self.transform = mat34Id() # no rotation required for HMD attachment
        if self.flip:
            self.transform[0][0] *= -1
        # assign position
        self.transform[0][3] = pos[0] * settings['Icon plane depth']
        self.transform[1][3] = pos[1] * settings['Icon plane depth']
        self.transform[2][3] = -settings['Icon plane depth']

        self.overlay.setOverlayTransformTrackedDeviceRelative(self.handle, 
                                                              openvr.k_unTrackedDeviceIndex_Hmd, 
                                                              self.transform)

class UIManager:
    def __init__(self) -> None:
        self.overlay = openvr.IVROverlay()
        self.rightHand = UIElement(self.overlay, "GOpy-R", "Right UI Element", 
                                   (settings['Normalised icon X position'], settings['Normalised icon Y position']))
        self.leftHand = UIElement(self.overlay, "GOpy-L", "Left UI Element", 
                                  (-settings['Normalised icon X position'], settings['Normalised icon Y position']), 
                                  flip = True)
        self.rID = 0
        self.lID = 0

        # set up timers
        self.rLastUpdate = time.monotonic()
        self.lLastUpdate = time.monotonic()

    def update(self):
        currTime = time.monotonic()
        if settings['Fade interval'] != 0:
            self.evaluateTransparencyFade(self.rightHand, self.rLastUpdate, currTime)
            self.evaluateTransparencyFade(self.leftHand, self.lLastUpdate, currTime)

    def rightHandUpdate(self, id):
        if self.rID != id and gestureDisableArr[id] == 0:
            self.rID = id
            self.rightHand.setImage(self.getImagePathFromId(id))
            self.rightHand.setTransparency(settings['Transparency'])
            self.rLastUpdate = time.monotonic()

    def leftHandUpdate(self, id):
        if self.lID != id and gestureDisableArr[id] == 0:
            self.lID = id
            self.leftHand.setImage(self.getImagePathFromId(id))
            self.leftHand.setTransparency(settings['Transparency'])
            self.lLastUpdate = time.monotonic()

    def getImagePathFromId(self, id):
        if id == 0:
            return PATH_NEUTRAL
        elif id == 1:
            return PATH_FIST
        elif id == 2:
            return PATH_OPENHAND
        elif id == 3:
            return PATH_POINT
        elif id == 4:
            return PATH_VICTORY
        elif id == 5:
            return PATH_ROCKANDROLL
        elif id == 6:
            return PATH_FINGERGUN
        elif id == 7:
            return PATH_THUMBSUP

    def evaluateTransparencyFade(self, hand, lastUpdate, currentTime):
        if (currentTime - lastUpdate) > settings['Fade time']:
            timeThroughInterval = currentTime - lastUpdate - settings['Fade time']
            fadeRatio = 1 - timeThroughInterval / settings['Fade interval']
            if fadeRatio < 0:
                fadeRatio = 0
            
            hand.setTransparency(fadeRatio * settings['Transparency'])

################################################################################

# main loop for updating the UI
async def mainLoop(uiMan):
    while True:
        startTime = time.monotonic()
        uiMan.update()
        
        sleepTime = (1 / UPDATE_RATE) - (time.monotonic() - startTime)
        if sleepTime > 0:
            await asyncio.sleep(sleepTime)

async def init_main():
    # load config file and handle settings
    global settings
    configPath = os.path.join(os.path.dirname(__file__), 'config.json')
    loadedSettings = {} # buffer for error handling
    try:
        with open(configPath) as json_file:
            loadedSettings = json.load(json_file)
    except IOError:
        print(f"GOpy: Could not find config file at {configPath}. Creating new config file.")
        with open(configPath, 'w') as outfile:
            json.dump(settings, outfile, indent=4)
        with open(configPath) as json_file:
            loadedSettings = json.load(json_file)
    settings = loadedSettings

    # populate gesture disable array
    global gestureDisableArr 
    gestureDisableArr = [0, settings["Disable fist"], 
                         settings["Disable openhand"], 
                         settings["Disable point"], 
                         settings["Disable victory"], 
                         settings["Disable rocknroll"], 
                         settings["Disable fingergun"], 
                         settings["Disable thumbsup"]]

    uiMan = UIManager()
    osc = OSCHandler(uiMan)

    await osc.initServer()

    await mainLoop(uiMan)    

if __name__ == '__main__':
    openvr.init(openvr.VRApplication_Overlay)

    asyncio.run(init_main())