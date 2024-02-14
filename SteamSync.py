import json
import pathlib
import re
import sys
import traceback
from typing import List, Tuple
import winreg
import os
from os import path
import PySimpleGUI as sg
import urllib3
import vdf
from PIL import Image

STEAM_API = "http://api.steampowered.com/"
KEY = "20F58DAB4E215359D7667DB18C99BD8D"
games_endpoint = f"{STEAM_API}IPlayerService/GetOwnedGames/v0001/?key={KEY}&format=json&include_appinfo=true&include_played_free_games=true&steamid="
id_endpoint = f"{STEAM_API}ISteamUser/ResolveVanityURL/v0001/?key={KEY}&vanityurl="
http = urllib3.PoolManager()


def get_steam_game_icons(local_users: List[Tuple[str, str]]):
    games_endpoint = f"{STEAM_API}IPlayerService/GetOwnedGames/v0001/?key={KEY}&format=json&include_appinfo=true&include_played_free_games=true&steamid="
    print("""This tool needs to know your Steam ID (long number).""")

    username, steam_id = determine_username_id(local_users)

    resolve_id = http.request("GET", games_endpoint + steam_id)
    body = json.loads(resolve_id.data.decode("utf-8"))
    if resolve_id.status != 200:
        print(f"Provided or resolved ID not working: {steam_id}")
        print(f"Please check ID manually & report on GitHub if the issue persists.")
    elif len(body["response"]) == 0:
        print(f"\nEmpty response from SteamAPI")
        print(f"{steam_id}'s game library is not publicly visible")
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Empty response from SteamAPI for user {username} ({steam_id}):\n")
            f.write(json.dumps(body))

        exit(-1)

    appid_to_icon = {
        str(game["appid"]): f"{game['img_icon_url']}.jpg"
        for game in body["response"]["games"]
    }

    return appid_to_icon


def determine_username_id(local_users: List[Tuple[str, str]]):
    username, steam_id = None, None

    if local_users:
        while True:
            options = "\n".join(
                f"{i+1}) {u[0]} ({u[1]})" for i, u in enumerate(local_users)
            )
            
            options_list = options.split()
            options_list.pop(0)
            
            layout = [
                [sg.Text("Multiple users found. Please select a user.")]        
            ]
            option_num = 1
            for i in range(len(options_list)):
                if i == 0:
                    pass
                elif i % 3 != 0:
                    continue 
                option = options_list[i]
                layout.append([sg.Button(f"{option_num}) {option}")])
                option_num += 1
            layout.append([sg.Button("Done"), sg.Cancel()])
            window = sg.Window("Select User", layout)
            popup = True
            option_num = 1
            while popup:
                event, values = window.read()
                if event in (sg.WINDOW_CLOSED, "Cancel"):
                    quit()
                for i in range(len(options_list)):
                    if i == 0:
                        pass
                    elif i % 3 != 0:
                        continue 
                    option = options_list[i]
                    if event == f"{option_num}) {option}":
                        selection = str(option_num)
                    option_num += 1
                if event == "Done":
                    try: 
                        idx = selection
                        break   
                    except:
                        sg.popup_error("No selection has been made!" )
            window.close()
            if idx.lower() == "x":
                break
            try:
                choice = int(idx)
                if choice > 0 and choice <= len(local_users):
                    username, steam_id = local_users[choice - 1]
                    break
            except:
                    pass
    if username is None or steam_id is None:
        username = input(
            "\nPlease enter your Steam ID, username (not nickname), or custom profile id: "
        )

        steam_id = resolve_steam_id_from_username(username)

        if steam_id is None:
            exit(-1)
    return username, steam_id


def resolve_steam_id_from_username(username):
    """
    Tries to resolve ID from username using ResolveVanityURL. On failure, see
    if the username provided was actually an ID already. On failure, return None.
    """

    # Assume username is not an ID
    resolve_id = http.request("GET", id_endpoint + username)
    body = json.loads(resolve_id.data.decode("utf-8"))
    steam_id = None
    if body["response"]["success"] == 1:
        steam_id = body["response"]["steamid"]
        return steam_id
    elif is_integer(username):
        # See if username is an ID
        resolve_id = http.request("GET", games_endpoint + username)
        body = json.loads(resolve_id.data.decode("utf-8"))
        if resolve_id.status == 200 and len(body["response"]) > 0:
            return username

    return None


def get_steam_library_path(steam_path: pathlib.Path) -> pathlib.Path:
    # Try and get the library index file as a sanity check for the right folder
    try:
        return pathlib.Path(
            [x for x in steam_path.glob("steamapps/libraryfolders.vdf")][0]
        )
    except:
        exit(-1)


def get_steam_local_user_ids(steam_path: pathlib.Path) -> List[Tuple[str, str]]:
    # Try and get the library index file as a sanity check for the right folder
    users = []
    try:
        login_file = list(steam_path.glob("config/loginusers.vdf"))
        if not login_file:
            return []

        with open(login_file[0]) as index_file:
            lib_vdf = vdf.load(index_file)

            for id_, data in lib_vdf.get("users", {}).items():
                if isinstance(data, dict) and data.get("AccountName"):
                    users.append((data["AccountName"], id_))

    except:
        print("Could not locate local users.")
    finally:
        return users


def get_steam_path():
    """
    Tries to get the Steam installation folder, or asks the user.
    This will also get the location to the library listings file,
    which forms part of the check to make sure it's the right folder.

    Returns a tuple of (steam_path, library_index_path)
    """

    # Search Registry
    try:
        hkey = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam"
        )
    except:
        hkey = None
        print(sys.exc_info())
    try:
        steam_path = winreg.QueryValueEx(hkey, "InstallPath")[0]
    except:
        steam_path = None
        print(sys.exc_info())
    winreg.CloseKey(hkey)

    # Ask the user if the registry was unhelpful
    if not steam_path:
        steam_path = input(
            "Failed to find Steam installation path, please provide the path e.g. C:\Program Files (x86)\Steam, ~/.local/steam, etc\n"
        )

    steam_path = pathlib.Path(steam_path)

    return steam_path


def get_library_folders(steam_path, library_index_path):
    """
    Reads the library index file `libraryfolders.vdf` to get a list of all
    Steam library locations on your system.

    Because of the lazy way in which the RegEx is written, it only supports
    up to 100 Steam libraries... but come on.

    Returns the library locations
    """

    libraries = []

    with open(library_index_path) as index_file:
        lib_vdf = vdf.load(index_file)

    for lib in lib_vdf.get("libraryfolders", {}).values():
        if isinstance(lib, dict) and lib.get("path"):
            path = pathlib.Path(lib["path"])
            libraries.append(path)

    libraries.append(steam_path)

    return sorted(libraries)


def get_installed_games(libraries, icons):
    """
    For each library, parse all the appmanifest_xxx.acf files for
    game names and install locations, where xxx is the appid of an installed game.

    Returns a dictionary of appid -> {name, location, icon, icon_hash, icon_ext}
    """

    # Horrible flattening of each manifest file
    manifests = [
        item
        for sublist in [
            [x for x in path.glob("steamapps/appmanifest_*.acf")] for path in libraries
        ]
        for item in sublist
    ]

    # We want to find the game name and install directory
    patterns = [re.compile('"name".+".+"'), re.compile('"installdir".+".+"')]
    games = dict()

    # Parse each manifest and build the games dict
    for m in manifests:
        try:
            with open(m.resolve(), encoding="utf-8") as acf:
                lines = acf.readlines()
                name, location = [
                    p.search("\n".join([l.strip() for l in lines])) for p in patterns
                ]

                if name and location:
                    appid = m.stem.split("_")[1]
                    name, location = [
                        field[0].replace('"', "").split("\t\t")[1]
                        for field in [name, location]
                    ]
                    location = m.parent / f"common/{location}"
                    try:
                        location.resolve(strict=True)
                    except:
                        continue
                    games[appid] = {
                        "name": name,
                        "location": location,
                        "icon": None,
                        "icon_hash": icons[appid].split(".")[0]
                        if appid in icons.keys()
                        else None,
                        "icon_ext": icons[appid].split(".")[1]
                        if appid in icons.keys()
                        else None,
                    }
                else:
                    print(
                        f"  Couldn't locate name or location for game {m}\n  Name: {name}\n  Location: {location}\n"
                    )

        except KeyboardInterrupt as e:
            raise
        except Exception as e:
            print("Unhandled exception when reading file", m, e)

    return games


def check_for_icons(games):
    """
    For each game, checks to see if an icon exists the  game by looking
    for an icon.ico in the game's installation directory
    """

    for appid, game in games.items():
        try:
            icon_path = pathlib.Path(game["location"] / f"{game['icon_hash']}.ico")
            games[appid]["icon"] = icon_path.resolve(strict=True)
        except Exception as e:
            continue


def get_icons(games):
    """
    This will attempt to download all missing icons from SteamDB and Steam's CDN
    It might fail, in which case the {appid -> icon} remains None
    """

    for appid, game in filter(lambda g: not g[1]["icon"], games.items()):
        print(f"  Downloading icon for {appid} ({game['name']})")
        try:
            if game["icon_hash"] is None:
                raise Exception(f"No Icon URL found for {appid} ({game['name']})")

            # Write the ico data to an icon file in the game's install dir
            icon_url = f"https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/{appid}/{game['icon_hash']}.{game['icon_ext']}"
            icon_path = pathlib.Path(game["location"] / f"{game['icon_hash']}.ico")
            with http.request("GET", icon_url, preload_content=False) as jpg_data, open(
                icon_path, "wb+"
            ) as ico_file:
                jpg = Image.open(jpg_data)
                jpg.save(icon_path)
            jpg_data.release_conn()

            # Set the icon location for the game
            games[appid]["icon"] = icon_path
        except KeyboardInterrupt:
            raise
        except Exception as e:
            with open("error_log.txt", "a", encoding="utf-8") as f:
                f.write(traceback.format_exc())


def create_shortcuts(games, create_with_missing, start_menu=False):
    """
    For each game, now create the URL shortcuts to steam://rungameid/{appid},
    set the icon if it exists, or blank if the user asks for icon-less shortcuts

    Returns the number of shortcuts created
    """

    if start_menu:
        s = pathlib.Path(
            path.expandvars(
                "%SystemDrive%\ProgramData\Microsoft\Windows\Start Menu\Programs"
            )
        )
        folder = s / "Steam Games"
    else:
        folder = pathlib.Path("./shortcuts")
    folder.mkdir(parents=True, exist_ok=True)
    count = 0
    iconpaths = []
    for appid, game in games.items():
        # Sanitise the game's name for use as a filename
        filename = re.sub(r'[\\/*?:"<>|]', "", game["name"]) + ".url"

        # Skip game if missing the icon and the user asked to
        # not create shortcuts with missing icons
        if not game["icon"] and not create_with_missing:
            continue
        ## add icon paths to a separate list
        iconpaths.append(game["icon"])
        # Write the shortcut file
        with open(folder / filename, "w+", encoding="utf-8") as shortcut:
            shortcut.write("[InternetShortcut]\n")
            shortcut.write("IconIndex=0\n")
            shortcut.write(f"URL=steam://rungameid/{appid}\n")
            shortcut.write(f"IconFile={game['icon']}\n")
        count += 1

    return (count, folder)


def is_integer(x):
    try:
        int(x)
        return True
    except:
        return False


def main():
    """
    Where the magic happens
    """

    # Get path to Steam and libraries
    steam_path = get_steam_path()
    library_path = get_steam_library_path(steam_path)
    libraries = get_library_folders(steam_path, library_path)
    local_users = get_steam_local_user_ids(steam_path)

    if not libraries:
        print("No libraries to check")
        exit(0)

    icons = get_steam_game_icons(local_users)

    # Show game and folder info to user
    games = get_installed_games(libraries, icons)
    print(
        f"Found {len(games)} game{'s' if len(games) > 1 else ''} in the following libraries:"
    )
    print("\n".join(map(lambda x: f"  {x}", libraries)))

    games_without_icon_hashes = [
        "  " + game["name"] for game in games.values() if game["icon_hash"] is None
    ]

    if games_without_icon_hashes:
        print(
            f"\nFound installed games ({len(games_without_icon_hashes)}) which don't belong to your account."
        )
        print("\n".join(games_without_icon_hashes))
        print(
            "Shortcuts for these games can still be created, but they will not have icons."
        )

    # Try and find any existing icons for the found games
    check_for_icons(games)
    found_icons = len([True for game in games.values() if game["icon"]])
    print(f"\nFound {found_icons} existing game icon{'s' if found_icons != 1 else ''}")
    # Ask the user if they'd like to download the missing icons
    # By default will download missing icons and create shortcuts with missing icons
    create_with_missing, try_download, start_menu = True, True, False
    missing = len(games) - found_icons
    if missing > 0:
        print(f"\nMissing icons for {missing} game{'s' if missing != 1 else ''}")
        try_download = "y".lower().strip() != "n"

    if try_download:
        get_icons(games)

    # Check for any icons that are still missing
    failed = [game["name"] for game in games.values() if not game["icon"]]
    if failed and try_download:
        print(
            f"\nFailed to acquire the following {len(failed)} icon{'s' if len(failed) != 1 else ''}"
        )
        print("\n".join(map(lambda x: f"  {x}", failed)))

    # Ask if the user would like to create shortcuts with missing icons
    create_with_missing = (
        "y".lower().strip() != "n"
    )

    start_menu = (
        "n".lower().strip()
        == "y"
    )

    # Create shortcuts, show some stats, and exit
    try:
        count, folder = create_shortcuts(games, create_with_missing, start_menu)
    except PermissionError:
        print(
            "\n\nTo add to the start menu, please run this tool from an elevated (admin) terminal"
        )
        print("Falling back to ./shortcuts")
        count, folder = create_shortcuts(games, create_with_missing)

    print(f"\nDone! Created {count} shortcut{'s' if count != 1 else ''}")
   
    layout = [
        [sg.Text('Steam Game'), sg.Input(key="-IN-"), sg.FileBrowse(initial_folder="shortcuts", file_types=(("Executable", "*.exe"),))],
        [sg.Text('Mod/App/Script'), sg.Input(key="-IN-"), sg.FileBrowse(initial_folder='%%USERPROFILE%%')],
        [sg.Button("Sync"), sg.Cancel()]
    ]

    window = sg.Window('SteamSync GUI', layout)

    while True:
        event, values = window.read()
        print(event, '\n', values, '\n')
        if event in (sg.WINDOW_CLOSED, "Cancel"):
            break
        if event == "Sync":        
            game = '"' + values["-IN-"] + '"'
            file = '"' + values["-IN-0"] + '"'
            for i in game:
                if i == '/':
                    game = game.replace(i, '\\')
            for i in file:
                if i == '/':
                    file = file.replace(i, '\\')
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            cd= os.getcwd()
            for i in cd:
                if i =='\\\\' :
                    cd = cd.replace(i, '\\')
                    
            
            success = False
            while success == False:
                try:
                    cmd = 'newsync.bat ' + game + ' ' + file
                    os.system(cmd)
                    sg.popup_ok_cancel('Sync Complete!', 'Press OK to continue or press Cancel to exit.')
                    success = True
                    break
                except:
                    sg.popup_error('Sync Failed!', '1 or more file(s) failed to sync.')

            

    window.close()
    ## End of main


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ke:
        print(ke)
    except Exception:
        print("Unexpected exception", traceback.print_exc())
