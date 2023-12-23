![alt text](https://github.com/armand0e/SteamSync/blob/main/imgs/banner.png?raw=true)
# ![alt text](https://github.com/armand0e/SteamSync/blob/main/imgs/logo32.png?raw=true) SteamSync
### Sync the startup and shutdown of any mod, app, script, or program with your steam games!
## Setup
1. Download the [latest release](https://github.com/armand0e/SteamSync/releases/latest) and extract the zip
2. Run setup.bat

## Usage

1. Launch *SteamSync.py*
2. Specify which programs you would like to sync

* In the first input box, browse for and select the .exe file of the steam game you would like to sync
* In the second input box, browse for and select the program you want to launch with your game.

*You can also just paste in the file path*

3. Press "Sync"        

**IMPORTANT: To use with the steam launcher, specify the following launch options for your game:**

        sync.vbs %COMMAND%

## Uninstall
To remove individual sync scripts:
* open the uninstall folder 
* run the .bat file for the sync you wish to remove (i.e. rocketleague_BakkesMod.bat)

To remove ALL sync scripts:
* Run *uninstall_all.bat*
