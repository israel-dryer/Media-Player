"""
    Bare Bones Media Player with Playlist
    Author      :   Israel Dryer
    Modified    :   2019-10-30
"""
import vlc
import PySimpleGUI as sg 
from sys import platform as PLATFORM

sg.change_look_and_feel('DarkBlue')

# media player gui
def btn(name):
    return sg. Button(name, size=(6, 1), pad=(1, 1), key=name.upper())

layout = [[sg.Input(default_text='Video URL or Local Path:', size=(30, 1), key='NEW'), btn('load')],
          [sg.Image('', size=(300, 170), key='VID_OUT')],
          [btn('previous'), btn('play'), btn('next'), btn('pause'), btn('stop')],
          [sg.Text('Load media to start', key='TIME')]]

window = sg.Window('Mini Player', layout, element_justification='center', finalize=True)

# media player object
inst = vlc.Instance()
list_player = inst.media_list_player_new()
media_list = inst.media_list_new([])
list_player.set_media_list(media_list)
player = list_player.get_media_player()
if PLATFORM.startswith('linus'):
    player.set_xwindow(window['VID_OUT'].Widget.winfo_id)
else:
    player.set_hwnd(window['VID_OUT'].Widget.winfo_id())

# main event loop
while True:
    event, values = window.read(timeout=1000)

    if event is None:
        break
    if event == 'PLAY':
        list_player.play()
    if event == 'PAUSE':
        list_player.pause()
    if event == 'STOP':
        list_player.stop()
    if event == 'NEXT':
        list_player.next()
        list_player.play()
    if event == 'PREVIOUS':
        list_player.previous() 
        list_player.previous() # 2 calls needed to get to prior??
        list_player.play()
    if event == 'LOAD':
        vid = values['NEW']
        if not 'Video URL' in vid and vid != '': 
            media_list.add_media(vid)
            list_player.set_media_list(media_list)
            window['NEW'].update(value = 'Video URL or Local Path:') # only add a legit submit

    # update elapsed time if there is a video loaded and the player is playing
    elapsed = "{:02d}:{:02d} / {:02d}:{:02d}".format(*divmod(player.get_time()//1000, 60), *divmod(player.get_length()//1000, 60))
    if player.is_playing():
        window['TIME'].update(value = elapsed)
    elif media_list.count() == 0:
        window['TIME'].update(value = 'Load media to start')
    else:
        window['TIME'].update(value = 'Ready to play media')