"""
    Demo design and functionality for a Media Player playlist builder
    Author      :   Israel Dryer, israel.dryer@gmail.com
    Modified    :   2019-10-23 
"""
import PySimpleGUI as sg

playlist = ["Song 1", "Song 2", "Song 3", "Song 4", "Song 5", "Song 6"]

def btn(image, key): 
    filename = './images/button_images/' + image + '.png'
    return sg.Button(image_filename=filename, button_color=('white', sg.DEFAULT_BACKGROUND_COLOR), 
        border_width=0, pad=(0,0), key=key)

col1 = [[btn('plus', 'PLUS')], [btn('minus', 'MINUS')], [btn('up', 'UP')], [btn('down', 'DOWN')]]
col2 = [[sg.Listbox(playlist, key='PLAYLIST', size=(50, 12))]]

layout = [[sg.Col(col1), sg.Col(col2)],[sg.Submit(size=(10, 2)), sg.Cancel(size=(10, 2))]]
window = sg.Window('Media Player :: Build Playlist', layout)

while True:
    event, values = window.read()
    if event in (None, 'Cancel'):
        break
    if event == 'PLUS':
        try:
            pos = playlist.index(values['PLAYLIST'].pop())+1
        except:
            pos = len(playlist)-1
        new_media = sg.popup_get_text('YouTube URL:')
        playlist.insert(pos, new_media)
        window['PLAYLIST'].update(values=playlist, set_to_index=pos)
    if event == 'MINUS':
        try:
            ix = playlist.index(values['PLAYLIST'].pop())
            playlist.pop(ix)
            pos = min(len(playlist)-1, ix)
            window['PLAYLIST'].update(values=playlist, set_to_index=pos)
        except:
            continue
    if event == 'UP':
        ix = playlist.index(values['PLAYLIST'].pop())
        pos = max(ix-1, 0)
        item = playlist.pop(ix)
        playlist.insert(pos, item)
        window['PLAYLIST'].update(values=playlist, set_to_index=pos)            
    if event == 'DOWN':
        ix = playlist.index(values['PLAYLIST'].pop())
        pos = min(ix + 1, len(playlist)-1)
        item = playlist.pop(ix)
        playlist.insert(pos, item)
        window['PLAYLIST'].update(values=playlist, set_to_index=pos)     
    if event == 'Submit':
        sg.popup_ok('Playlist added to media player')       
        break 
    else:
        print(event, values) 