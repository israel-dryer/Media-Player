"""     
    Mini VLC media player for local and online streaming media
    Author      :   Israel Dryer
    Modified    :   2019-11-22   
"""
import PySimpleGUI as sg
from sys import platform as PLATFORM
import vlc
import pafy

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

def add_media(window, media_list, instance, list_player):
    """ add new track to list player with meta data if available """
    url = sg.PopupGetFile('Browse for local media or enter URL:', title='Load Media')
    if url is None:
        return
    try:
        vid = pafy.new(url)
        media = instance.media_new(vid.getbest().url)
        media.set_meta(0, vid.title)
    except:
        media = instance.media_new(url)
        media.set_meta(0, url.replace('\\','/').split('/').pop()) # filename
    finally:
        media_list.add_media(media)
        if media_list.count() == 1:
            list_player.play()

def track_info(window, player):
    """ show author, title, and elasped time if video is loaded and playing """
    time_elapsed = "{:02d}:{:02d}".format(*divmod(player.get_time()//1000, 60))
    time_total = "{:02d}:{:02d}".format(*divmod(player.get_length()//1000, 60))
    if player.is_playing():
        window['INFO'].update("{}".format(player.get_media().get_meta(0)))
        window['TIME_ELAPSED'].update(time_elapsed)
        window['TIME'].update(player.get_position())
        window['TIME_TOTAL'].update(time_total)
    else:
        try:
            window['INFO'].update("{}".format(player.get_media().get_meta(0)))
        except:
            window['INFO'].update('LOAD media to Start')

# ----- GUI ------------------------------------------------------------------
def btn(name, **kwargs):
    return sg.Button(name, size=(7, 1), pad=(1, 1), key=name.upper(), **kwargs)

def create_gui():
    """ create media player gui to handle vlc media player output """
    sg.change_look_and_feel('DarkBlue')
    layout = [[sg.Text('LOAD media to Start', size=(40, 1), justification='left', font=(sg.DEFAULT_FONT, 10), key='INFO')],
              [sg.Image('images/default.png', size=(426, 240), key='VID_OUT')],
              [sg.Text('00:00', key='TIME_ELAPSED'), 
               sg.Slider(range=(0, 1), enable_events=True, resolution=0.0001, disable_number_display=True, background_color='#83D8F5', orientation='h', key='TIME'),
               sg.Text('00:00', key='TIME_TOTAL')],
              [btn('previous'), btn('play'), btn('next'), btn('pause'), btn('stop'), btn('media', button_color=('#000000','#7EE8F5'), focus=True)]]
    window = sg.Window('Mini Player', layout, element_justification='center', finalize=True)
    window['TIME'].expand(expand_x=True)  
    window['INFO'].expand(expand_x=True)
    return window

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
        if event == 'MEDIA':
            add_media(window, media_list, instance, list_player)
        if event == 'STOP':
            player.stop()
            window['TIME_ELAPSED'].update('00:00')
        if event == 'TIME':
            player.set_position(values['TIME'])
            window['TIME_ELAPSED'].update("{:02d}:{:02d}".format(*divmod(int(player.get_length()*values['TIME'])//1000, 60)))