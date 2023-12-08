#!/usr/bin/env python3
import os 
import PySimpleGUI as sg

layout = [
    [sg.Text('Steam Game'), sg.Input(key="-IN-"), sg.FileBrowse(initial_folder="C:/Program Files (x86)/Steam/steamapps/common", file_types=(("Executable", "*.exe"),))],
    [sg.Text('Mod/App/Script'), sg.Input(key="-IN-"), sg.FileBrowse(initial_folder='C:/Users')],
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
