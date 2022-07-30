# GOpy - VRChat Gesture Overlay in Python
This Python script reads your current VRChat gestures via OSC and creates a SteamVR overlay displaying them on screen.
Primarily designed for Index users, where the VRChat implementation of the Knuckles controllers often results in gestures not matching what you're doing in real life.
This works for **any _3.0_** avatar, irrespective of if you made it or not. 

![Example of UI](https://github.com/MeroFune/GOpy/blob/main/example.PNG)

SteamVR overlays (see the [FAQ](https://hello.vrchat.com/blog/vrchat-security-update)) and OSC are supported by VRChat and are not classified as mods. 
Replicates the behaviour of a mod created by [ImTiara](https://github.com/ImTiara).

## Usage guide
Download a .zip containing the latest release from the [releases page](https://github.com/MeroFune/GOpy/releases) and run GOpy.exe within the extracted folder - You do not need to install anything else for it to run this way.
It is recommended to only launch GOpy after SteamVR is fully initialised. 

To ensure the app works, please do the following:
- Enable OSC in VRChat via the action menu
- Configure the VRChat OSC IP and corresponding listening port as necessary in the settings (default corresponds to the VRChat defaults)
- Use any Avatar 3.0 avatar (2.0 avatars do not support OSC)

The app will keep running in the background until you manually close it yourself. 
Restarting VRChat, or launching the app after VRC and SteamVR are already open, will not cause any errors, however launching before SteamVR initialises may cause issues if you do not have SteamVR auto-start enabled.
If you keep the app running while playing other VR games, then the gestures will auto-fade and will not appear again until VRChat is launched and a new gesture is triggered.

## Settings
Configuration settings are stored in a `config.json` file in the same directory as the application. 
On first launch, and if a config file doesn't exist, then the script will generate one using the default parameters.
Settings are as follows:
- `VRC OSC IP` - The IP address corresponding to VRChat's OSC protocol
- `VRC OSC port` - The port corresponding to where VRChat sends OSC messages to
- `Colour` - Colour of the overlay as an `[R, G, B]` array
- `Transparency` - The maximum transparency/ alpha of the overlay
- `Normalised icon X position` - X position of the _right_ overlay, normalised by the plane depth. Left is mirrored
- `Normalised icon Y position` - Y position of the _right_ overlay, normalised by the plane depth. Left is mirrored
- `Icon plane depth` - Distance of the plane where overlays are rendered from the HMD in meters
- `Normalised icon width` - Width of the overlay icons, normalised by the plane depth
- `Fade time` - Time in seconds until the overlay begins to fade
- `Fade interval` - Time in seconds over which the overlay fades. Set to 0 to disable fading
- `Disable XXXX` - Set to non-zero to disable the gesture XXXX from showing in overlay when it is detected. Used if you accidentally use certain gestures often and don't want them to be shown. ie, to disable fist set `"Disable fist": 1`, to disable point set `"Disable point": 1`.

## Build requirements
To run the script from source via Python, you need the following:
- Python 3.6+ (remove f strings to use 3.5+)
- numpy
- python-osc 
- pyopenvr 
These can be partially found in `requirements_build_env.txt`.

Calling `pip install  -r requirements_build_env.txt` installs all requirements, and a fork of pyopenvr that allows building from executable.

Building an executable from source has further requirements:

### Creating an executable
Due to issues packaging, and that pyopenvr is no longer maintained, a [custom fork](https://github.com/Greendayle/pyopenvr) of pyopenvr is required. 
To install this (and all required dependencies) run `batch.bat` to install all dependencies and create a build.

## Credits
- Original idea and gesture images courtesy of [ImTiara](https://github.com/ImTiara)
- [Greendayle](https://github.com/Greendayle) for general assistance learning the SteamVR api and setting up the pyinstaller
