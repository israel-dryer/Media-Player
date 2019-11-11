"""
    Bare Bones Media Player with Playlist
    Uses the VLC player to playback local files and YouTube streams.
    
    Author      :   Israel Dryer
    Modified    :   2019-11-5
"""
import vlc
import pafy
import PySimpleGUI as sg 
from sys import platform as PLATFORM

sg.change_look_and_feel('DarkBlue')

# media player gui
def btn(name):
    return sg. Button(name, size=(6, 1), pad=(1, 1), key=name.upper())

menu = [['File', ['Exit'], ['Playlist', []]
tracks = menu[1][1]

layout = [[sg.Menu(menu, key='MENU')],
          [sg.Input(default_text='Video URL or Local Path:', size=(30, 1), key='NEW'), btn('load')],
          [sg.Image('', size=(300, 170), key='VID_OUT')],
          [btn('previous'), btn('play'), btn('next'), btn('pause'), btn('stop')],
          [sg.Text('Load media to start', size=(40, 2), justification='center', font=(sg.DEFAULT_FONT, 10), key='TIME')]]

window = sg.Window('Mini Player', layout, element_justification='center', finalize=True)

# media player object
inst = vlc.Instance()
list_player = inst.media_list_player_new()
media_list = inst.media_list_new([])
list_player.set_media_list(media_list)
player = list_player.get_media_player()
if PLATFORM.startswith('linux'):
    player.set_xwindow(window['VID_OUT'].Widget.winfo_id())
else:
    player.set_hwnd(window['VID_OUT'].Widget.winfo_id())

def add_media(url, window=window, media_list=media_list, instance=inst):
    """ add media to media_list player """
    vid = pafy.new(url)
    best = vid.getbest()
    media = instance.media_new(best.url)
    media.set_meta(0, vid.title)
    media.set_meta(1, vid.author)
    media.set_meta(6, vid.description)
    media.set_meta(10, url)
    media_list.add_media(media)
    menu[0][1].append(vid.title)
    window['MENU'].update(menu_definition=menu)

def get_meta(type: int, player=player) -> str:
    """ retrieve meta data on currently playing item """
    try:
        media = player.get_media()
        meta = media.get_meta(type)
        return meta
    except:
        return

# main event loop
while True:
    event, values = window.read(timeout=1000)

    if event in (None, 'Exit'):
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
            add_media(values['NEW'])
            window['NEW'].update('Video URL or Local Path:') # only add a legit submit
    if event in tracks:
        list_player.play_item_at_index(tracks.index(event))

    # show channel, title, and elasped time if there is a video loaded and the player is playing
    elapsed = "{:02d}:{:02d} / {:02d}:{:02d}".format(*divmod(player.get_time()//1000, 60), *divmod(player.get_length()//1000, 60))
    if player.is_playing():
        message = "{} | {}\n{}".format(get_meta(1), elapsed, get_meta(0)) 
        window['TIME'].update(message)
        #window['TIME'].set_tooltip(get_meta(6)) # vid description in tooltip?
    elif media_list.count() == 0:
        window['TIME'].update('Load media to start')
    else:
        window['TIME'].update('Press Play to Start')