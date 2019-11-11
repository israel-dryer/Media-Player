"""
    Bare Bones Media Player with Playlist
    Uses the VLC player to playback local and online media.
    
    Author      :   Israel Dryer
    Modified    :   2019-11-11
"""
import vlc
import pafy
import PySimpleGUI as sg
from sys import platform as PLATFORM

sg.change_look_and_feel('DarkBlue')

# ----- MEDIA PLAYER ---------------------------------------------------------
def create_media_player(window):
    instance = vlc.Instance()
    list_player = instance.media_list_player_new()
    media_list = instance.media_list_new([])
    list_player.set_media_list(media_list)
    player = list_player.get_media_player()
    
    if PLATFORM.startswith('linux'):
        player.set_xwindow(window['VID_OUT'].Widget.winfo_id())
    else:
        player.set_hwnd(window['VID_OUT'].Widget.winfo_id())

    return (instance, list_player, media_list, player)

def add_media(url, window, media_list, instance):
    """ add new media to playlist """
    try:
        vid = pafy.new(url)
        best = vid.getbest()
        media = instance.media_new(best.url)
        media.set_meta(0, vid.title)
        media.set_meta(1, vid.author)
    except:
        media = instance.media_new(url)
        media.set_meta(0, url.replace('\\','/').split('/').pop()) # filename
        media.set_meta(1, 'Local Media')
    finally:
        media.set_meta(10, url)
        media_list.add_media(media)

def track_meta(meta_type, player):
    """ retrieve meta data on current item """
    try:
        media = player.get_media()
        meta = media.get_meta(meta_type)
        return meta
    except:
        return

def track_next(list_player):
    list_player.next()
    list_player.play()

def track_previous(list_player):
    list_player.previous() # return to beg of current track
    list_player.previous() # go to prior track
    list_player.play() # begin play of prior track

def track_load(values, window, media_list, instance):
    new_media = values['SUBMIT_NEW']
    if not 'URL' in new_media and new_media != '':
        add_media(new_media, window, media_list, instance)
        window['SUBMIT_NEW'].update('URL or Local Path:')

def track_info(window, player):
    """ show channel, title, and elasped time if there is a video loaded and 
        the player is playing """
    time_elapsed = divmod(player.get_time()//1000, 60)
    time_total = divmod(player.get_length()//1000, 60)
    time_format = "{:02d}:{:02d} / {:02d}:{:02d}".format(*time_elapsed, *time_total)
    if player.is_playing():
        message = "{} | {}\n{}".format(track_meta(1, player), time_format, track_meta(0, player))
        window['INFO'].update(message)
    elif media_list.count() == 0:
        window['INFO'].update('Load media to start')
    else:
        window['INFO'].update('Press PLAY to Start')

# ----- GUI ------------------------------------------------------------------
def btn(name):
    return sg.Button(name, size=(6, 1), pad=(1, 1), key=name.upper())

def create_gui():
    layout = [
        [sg.Input(default_text='URL or Local Path:', size=(30, 1), key='SUBMIT_NEW'), btn('load')],
        [sg.Image('', size=(300, 170), key='VID_OUT')],
        [btn('previous'), btn('play'), btn('next'), btn('pause'), btn('stop')],
        [sg.Text('Load media to start', size=(40, 2), justification='center', font=(sg.DEFAULT_FONT, 10), key='INFO')]]

    window = sg.Window('Mini Player', layout, element_justification='center', finalize=True)
    return window


if __name__ == '__main__':
    # create media player objects
    window = create_gui()
    instance, list_player, media_list, player = create_media_player(window)

    while True:
        event, values = window.read(timeout=100)

        if event is None:
            break
        if event == 'PLAY':
            list_player.play()
        if event == 'PAUSE':
            list_player.pause()
        if event == 'NEXT':
            track_next(list_player)
        if event == 'PREVIOUS':
            track_previous(list_player)
        if event == 'LOAD':
            track_load(values, window, media_list, instance)
        
        track_info(window, player)