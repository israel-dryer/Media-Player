"""     
    VLC media player for local and online streaming media
    Author      :   Israel Dryer
    Modified    :   2019-11-30
"""
import vlc
import pafy
import PySimpleGUI as sg
from sys import platform as PLATFORM
from os import listdir

# ----- MISC DEFAULT SETTINGS ------------------------------------------------
WINDOW_SIZE = (1280, 720)
SCALE = 0.5
VIDEO_SIZE = tuple([x * SCALE for x in WINDOW_SIZE])

THEME = 'DarkBlue'
sg.change_look_and_feel(THEME)
DEFAULT_BG_COLOR = sg.LOOK_AND_FEEL_TABLE[THEME]['BACKGROUND']

# ----- IMAGES ---------------------------------------------------------------
PATH = './images/'
BUTTON_PATH = PATH + 'button_images/win_white/'
BUTTONS = {img[:-4].upper(): BUTTON_PATH + img for img in listdir(BUTTON_PATH)}
DEFAULT_IMG = PATH + 'default.png'
ICON = PATH + 'player.ico'

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


def add_media(instance, list_player, media_list, window):
    """ add new track to list player with meta data if available """
    global track_num, track_cnt
    url = sg.PopupGetFile('Browse for local media or enter URL:', title='Load Media')
    if url is None:
        return
    try:
        vid = pafy.new(url)
        media = instance.media_new(vid.getbest().url)
        media.set_meta(0, vid.title)
        media.set_meta(1, vid.author)
        playlist_menu_add_track(vid.title)
    except:
        media = instance.media_new(url)
        media.set_meta(0, url.replace('\\','/').split('/').pop()) # filename
        media.set_meta(1, 'Local Media')
        playlist_menu_add_track('Local Media')
    finally:
        media.set_meta(10, url)
        media_list.add_media(media)
        track_cnt = media_list.count()
        if track_cnt == 1:
            track_num = 1
            list_player.play()


def track_meta(meta_type, player):
    """ retrieve saved meta data from tracks in media list """
    media = player.get_media()
    return media.get_meta(meta_type)


def trunc(string, chars):
    """ truncate string to a set number of characters """
    if len(string) > chars:
        return string[:chars] + "..."
    else:
        return string


def track_info(window, player, track_num, track_cnt):
    """ show author, title, and elasped time if video is loaded and playing """
    time_elapsed = "{:02d}:{:02d}".format(*divmod(player.get_time()//1000, 60))
    time_total = "{:02d}:{:02d}".format(*divmod(player.get_length()//1000, 60))
    if player.is_playing():
        message = "{}\n{}".format(track_meta(1, player).upper(), track_meta(0, player))
        window['INFO'].update(message)
        window['TIME_ELAPSED'].update(time_elapsed)
        window['TIME'].update(player.get_position())
        window['TIME_TOTAL'].update(time_total)
        window['TRACKS'].update('{} of {}'.format(track_num, track_cnt))
    elif media_list.count() == 0:
        window['INFO'].update('Open a FILE, STREAM, or PLAYLIST to begin')
    else:
        window['INFO'].update('Press PLAY to Start')


def play_video(window, list_player):
    list_player.play()
    window['PLAY'].update(image_filename=BUTTONS['PLAY_ON'])
    window['PAUSE'].update(image_filename=BUTTONS['PAUSE_OFF'])


def stop_video(window, player):
    player.stop()
    window['PLAY'].update(image_filename=BUTTONS['PLAY_OFF'])  
    window['PAUSE'].update(image_filename=BUTTONS['PAUSE_OFF'])
    window['TIME'].update(value=0)
    window['TIME_ELAPSED'].update('00:00')


def pause_video(window, player, media_list):
    window['PAUSE'].update(image_filename=BUTTONS['PAUSE_ON'] if player.is_playing() else BUTTONS['PAUSE_OFF'])
    window['PLAY'].update(image_filename=BUTTONS['PLAY_OFF'] if player.is_playing() else BUTTONS['PLAY_ON'])        
    player.pause()


def skip_next(list_player):
    global track_cnt, track_num
    if not track_cnt == track_num:
        track_num +=1
    list_player.next()


def skip_previous(list_player):
    global track_cnt, track_num
    if not track_num == 1:
        track_num -= 1
    list_player.previous()


def toggle_sound(window, player):
    window['SOUND'].update(image_filename=BUTTONS['SOUND_ON'] if player.audio_get_mute() else BUTTONS['SOUND_OFF'])
    player.audio_set_mute(not player.audio_get_mute())    


# ----- PLAYLIST -------------------------------------------------------------

def playlist_create_from_file(instance, window):
    """ open text file and load to new media list """
    global track_cnt, track_num, media_list, list_player
    filename = sg.popup_get_file('navigate to playlist', title='Create New Playlist', no_window=True)
    if filename is not None:
        with open(filename, 'r') as f:
            media_list = instance.media_list_new([])
            try:
                playlist = f.read().splitlines()
            except:
                sg.popup_error('Not able to create playlist from selected file.', title='Playlist Error')
                return

        for url in playlist:
            try:
                vid = pafy.new(url)
                media = instance.media_new(vid.getbest().url)
                media.set_meta(0, vid.title)
                media.set_meta(1, vid.author)
                playlist_menu_add_track(vid.title)
            except:
                media = instance.media_new(url)
                media.set_meta(0, url.replace('\\','/').split('/').pop()) # filename
                media.set_meta(1, 'Local Media')
                playlist_menu_add_track('Local Media')
            finally:
                media.set_meta(10, url)
                media_list.add_media(media)

        track_cnt = media_list.count()
        list_player.set_media_list(media_list)
        track_num = 1                
        window['MENU'].update(menu_definition=menu)
        list_player.play()


def playlist_menu_add_track(name):
    global menu
    menu[2][1][1].extend([name])


# ----- GUI ------------------------------------------------------------------
menu = [
    ['File', ['Load &Media', 'Load &Playlist', '---', 'Exit']],
    ['Controls', ['Play', 'Pause', 'Stop','---','Skip Next', 'Skip Previous']],
    ['Playlist', ['Active Playlist', ['---'], '---', 'Save New Playlist', 'Create from File', 'Edit Active Playlist']],
    ['Library', ['Edit Library']],
    ['About']]

def btn(key, image):
    ''' create player buttons '''
    return sg.Button(image_filename=image, border_width=0, pad=(0, 0), key=key, button_color=('white', DEFAULT_BG_COLOR))


def create_gui(menu):
    ''' create a gui instance '''
    col1 = [
        [btn('SKIP PREVIOUS', BUTTONS['START']), btn('PAUSE', BUTTONS['PAUSE_OFF']), 
         btn('PLAY', BUTTONS['PLAY_OFF']), btn('STOP', BUTTONS['STOP']), 
         btn('SKIP NEXT', BUTTONS['END']), btn('SOUND', BUTTONS['SOUND_ON'])]]

    col2 = [[sg.Text('Open a FILE, STREAM, or PLAYLIST to begin', size=(45, 3), font=(sg.DEFAULT_FONT, 8), pad=(0, 5), key='INFO')]]

    main_layout = [
        [sg.Menu(menu, key='MENU')],
        [sg.Image(filename=DEFAULT_IMG, pad=(0, 5), size=VIDEO_SIZE, key='VID_OUT')],
        [sg.Text('00:00', key='TIME_ELAPSED'), 
         sg.Slider(range=(0, 1), enable_events=True, resolution=0.0001, disable_number_display=True, background_color='#83D8F5', orientation='h', key='TIME'),
         sg.Text('00:00', key='TIME_TOTAL'),
         sg.Text('        ', key='TRACKS')], 
        [sg.Column(col1), sg.Column(col2)]]
    
    window = sg.Window('VLC Media Player', main_layout, element_justification='center', finalize=True)
    window['TIME'].expand(expand_x=True)
    return window


if __name__ == '__main__':
    window = create_gui(menu)
    instance, list_player, media_list, player = create_media_player(window)
    track_num, track_cnt = (0, 0)
    while True:
        event, values = window.read(timeout=1000)
        track_info(window, player, track_num, track_cnt)
        if event in (None, 'Exit'):
            break
        if event in ('PLAY', 'Play'):
            play_video(window, list_player)
        if event in ('PAUSE', 'Pause'):
            pause_video(window, player, media_list)
        if event in ('SKIP NEXT', 'Skip Next'):
            skip_next(list_player)
        if event in ('SKIP PREVIOUS', 'Skip Previous'):
            skip_previous(list_player)
        if event in ('STOP', 'Stop'):
            stop_video(window, player)
        if event == 'SOUND':
            toggle_sound(window, player)
        if event == 'TIME':
            player.set_position(values['TIME'])
        if event == 'Load Media':
            add_media(instance, list_player, media_list, window)
        if event == 'Create from File':
            playlist_create_from_file(instance, window)
        else:
            print(event, values)