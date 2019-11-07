"""
    Test program to demo the use of the menu as a functional playlist
    Author      :   Israel Dryer
    Modified    :   2019-11-06

"""

import PySimpleGUI as sg 

menu = [['File', ['Exit']],
        ['Playlist', ['Track1',['Delete::Track1', '---', 'Move Up::Track1', 'Move Down::Track1'], 
                      'Track2',['Delete::Track2', '---', 'Move Up::Track2', 'Move Down::Track2'],
                      'Track3',['Delete::Track3', '---', 'Move Up::Track3', 'Move Down::Track3']]]]

layout = [[sg.Menu(menu, key='MENU')],
          [sg.Button('Add Track', pad=(25, 25), size=(20, 2))]]

window = sg.Window('Menu Playlist App', layout)

def get_tracks(menu):
    """ get a list of tracks from the playlist menu """
    playlist = menu[1][1]
    return [track for track in playlist if isinstance(track, str)]

def add_track(window, track_cnt):
    track_name = 'Track' + str(next(track_cnt))
    track_menu = [f'Delete::{track_name}', '---', f'Move Up::{track_name}', f'Move Down::{track_name}'] 
    menu[1][1].extend([track_name, track_menu])
    window['MENU'].update(menu_definition=menu)

def get_index(item):
    """ find the index of track """
    tracks = get_tracks(menu)
    return tracks.index(item) * 2

def delete_track(track):
    """ delete a track from the playlist """
    ix = get_index(track)
    del(menu[1][1][ix:ix+2])

def move_up_track(track):
    """ move track up the list """
    ix = get_index(track)
    mv_track = menu[1][1][ix:ix+2]
    if ix == 0:
        return
    else:
        del(menu[1][1][ix:ix+2])
        menu[1][1].insert(ix-2, mv_track[0])
        menu[1][1].insert(ix-1, mv_track[1])

def move_down_track(track):
    """ move track down the list """
    ix = get_index(track)
    mv_track = menu[1][1][ix:ix+2]
    if ix == len(menu[1][1])-1:
        return
    else:
        del(menu[1][1][ix:ix+2])
        menu[1][1].insert(ix+2, mv_track[0])
        menu[1][1].insert(ix+3, mv_track[1])        

tracks = get_tracks(menu)
track_cnt = iter(range(4, 100))

while True:
    event, values = window.read()
    if event in(None, 'Exit'):
        break
    if event == 'Add Track':
        add_track(window, track_cnt)
        tracks = get_tracks(menu)
    if event in tracks:
        print(event, values)
    if '::' in event:
        action, track = event.split('::')
        print(action, track)
        if action == 'Delete':
            delete_track(track)
        if action == 'Move Up':
            move_up_track(track)
        if action == 'Move Down':
            move_down_track(track)            
        
        window['MENU'].update(menu_definition=menu)

