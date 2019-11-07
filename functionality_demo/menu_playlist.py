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
          [sg.Input('enter track name', size=(25, 1), key='TRACK')],
          [sg.Button('Add Track', pad=(25, 25), size=(20, 2))]]

window = sg.Window('Menu Playlist App', layout, element_justification='center')

def tracks_list(menu):
    """ get a list of tracks from the playlist menu """
    playlist = menu[1][1]
    return [track for track in playlist if isinstance(track, str)]

def track_add(name, window):
    trackmenu = [f'Delete::{name}', '---', f'Move Up::{name}', f'Move Down::{name}'] 
    menu[1][1].extend([name, trackmenu])
    window['MENU'].update(menu_definition=menu)

def track_index(item):
    """ find the index of track """
    tracks = tracks_list(menu)
    return tracks.index(item) * 2

def track_delete(track):
    """ delete a track from the playlist """
    ix = track_index(track)
    del(menu[1][1][ix:ix+2])

def track_mv_up(track):
    """ move track up the list """
    ix = track_index(track)
    mv_track = menu[1][1][ix:ix+2]
    if ix == 0:
        return
    else:
        del(menu[1][1][ix:ix+2])
        menu[1][1].insert(ix-2, mv_track[0])
        menu[1][1].insert(ix-1, mv_track[1])

def track_mv_down(track):
    """ move track down the list """
    ix = track_index(track)
    mv_track = menu[1][1][ix:ix+2]
    if ix == len(menu[1][1])-1:
        return
    else:
        del(menu[1][1][ix:ix+2])
        menu[1][1].insert(ix+2, mv_track[0])
        menu[1][1].insert(ix+3, mv_track[1])        

tracks = tracks_list(menu)

while True:
    event, values = window.read()
    if event in(None, 'Exit'):
        break
    if event == 'Add Track':
        track_add(values['TRACK'], window)
        tracks = tracks_list(menu)
    if event in tracks:
        print(event, values)
    if '::' in event:
        action, track = event.split('::')
        print(action, track)
        if action == 'Delete':
            track_delete(track)
        if action == 'Move Up':
            track_mv_up(track)
        if action == 'Move Down':
            track_mv_down(track)            
        
        window['MENU'].update(menu_definition=menu)

