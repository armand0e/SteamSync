# SteamSync
### Sync the startup and shutdown of any mod, app, or script with your steam games!
## Setup
1. Download the [latest release](https://github.com/armand0e/SteamSync/releases/latest) (the Source Code zip) and extract the zip
2. Run setup.bat

## Usage

1. Launch *SteamSync.py*
2. Specify both files

* In the first input box, browse for and select the .exe file of the steam game you would like to sync
* In the second input box, browse for and select the program you want to launch with your game.
* *You can also just paste the file path for both files into the provided text box*

3. Press "Sync"        

**To use with the steam launcher, specify the following launch options for your game:**

        sync.vbs %COMMAND%

## Uninstall
To remove individual sync scripts:
* open the uninstall folder 
* run the .bat file for the sync you wish to remove (i.e. rocketleague_BakkesMod.bat)

To remove ALL sync scripts:
* Run *uninstall_all.bat*
