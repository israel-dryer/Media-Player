"""     
    Mini VLC media player for local and online streaming media
    Author      :   Israel Dryer
    Modified    :   2019-11-12                                           
"""
import vlc
import pafy
import PySimpleGUI as sg
from sys import platform as PLATFORM
sg.change_look_and_feel('DarkBlue')

# ----- MEDIA PLAYER ---------------------------------------------------------
def create_media_player(window):
    """ create all vlc objects for list media player """
    instance = vlc.Instance()
    list_player = instance.media_list_player_new()
    media_list = instance.media_list_new([])
    list_player.set_media_list(media_list)
    player = list_player.get_media_player()
    # platform specific adjustments for window handler
    if PLATFORM.startswith('linux'):
        player.set_xwindow(window['VID_OUT'].Widget.winfo_id())
    else:
        player.set_hwnd(window['VID_OUT'].Widget.winfo_id())
    return (instance, list_player, media_list, player)

def add_media(url, window, media_list, instance):
    """ add new track to list player with meta data if available """
    try:
        vid = pafy.new(url)
        media = instance.media_new(vid.getbest().url)
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
    """ retrieve saved meta data from tracks in media list """
    media = player.get_media()
    return media.get_meta(meta_type)

def track_load(values, window, media_list, instance):
    """ add new track from url or path in user input element """
    new_media = values['SUBMIT_NEW']
    if not 'URL' in new_media and new_media != '':
        add_media(new_media, window, media_list, instance)
        window['SUBMIT_NEW'].update('URL or Local Path:')

def track_info(window, player):
    """ show author, title, and elasped time if video is loaded and playing """
    time_elapsed = divmod(player.get_time()//1000, 60)
    time_total = divmod(player.get_length()//1000, 60)
    time_format = "{:02d}:{:02d} / {:02d}:{:02d}".format(*time_elapsed, *time_total)
    # update the track info based on load and play status
    if player.is_playing():
        message = "{} | {}\n{}".format(track_meta(1, player), time_format, track_meta(0, player))
        window['INFO'].update(message)
    elif media_list.count() == 0:
        window['INFO'].update('LOAD media to Start')
    else:
        window['INFO'].update('Press PLAY to Start')

# ----- GUI ------------------------------------------------------------------
def btn(name):
    """ create gui buttons with standard parameters """
    return sg.Button(name, size=(6, 1), pad=(1, 1), key=name.upper())

def create_gui():
    """ create media player gui to handle vlc media player output """
    layout = [
        [sg.Input(default_text='URL or Local Path:', size=(30, 1), key='SUBMIT_NEW'), btn('load')],
        [sg.Image('', size=(426, 240), key='VID_OUT')],
        [btn('previous'), btn('play'), btn('next'), btn('pause'), btn('stop')],
        [sg.Text('LOAD media to Start', size=(40, 2), justification='center', font=(sg.DEFAULT_FONT, 10), key='INFO')]]
    return sg.Window('Mini Player', layout, element_justification='center', finalize=True)

if __name__ == '__main__':
    window = create_gui()
    instance, list_player, media_list, player = create_media_player(window)
    while True:
        event, values = window.read(timeout=1000)
        track_info(window, player)
        if event is None:
            break
        if event == 'PLAY':
            list_player.play()
        if event == 'PAUSE':
            list_player.pause()
        if event == 'NEXT':
            list_player.next()
        if event == 'PREVIOUS':
            list_player.previous()
        if event == 'LOAD':
            track_load(values, window, media_list, instance)