"""
    Media Player for local and streaming online videos. This is the TUTORIAL version and will
    remain relatively simple and straight-forward. The standard version will continue to be
    developed in the future for my own personal learning and curiosity.

    Author:     Israel Dryer, israel.dryer@gmail.com
    Modified:   10/22/2019
"""
import PySimpleGUI as sg
import vlc
import pafy
from os import listdir
from sys import platform as PLATFORM

# ------ CHECK OS ------------------------------------------------------------------------------- #
_isMacOS   = PLATFORM.startswith('darwin')
_isWindows = PLATFORM.startswith('win')
_isLinux = PLATFORM.startswith('linux')

# ------ MISC DEFAULT SETTINGS ------------------------------------------------------------------ #
DEFAULT_URL = 'https://www.youtube.com/watch?v=jE-SpRI3K5g'

WINDOW_SIZE = (1280, 720)
SCALE = 0.5
VIDEO_SIZE = tuple([x * SCALE for x in WINDOW_SIZE])

THEME = 'DarkBlue'
sg.change_look_and_feel(THEME)
DEFAULT_BG_COLOR = sg.LOOK_AND_FEEL_TABLE[THEME]['BACKGROUND']

# ------ IMAGES --------------------------------------------------------------------------------- #
PATH = './images/'
BUTTONS = {img[:-4].upper(): PATH + 'button_images/square_white/' + img for img in listdir(PATH + 'button_images')}
DEFAULT_IMG = PATH + 'default.png'
ICON = PATH + 'player.ico'

# ------ MEDIA PLAYER---------------------------------------------------------------------------- #
def vlc_player(window):
    ''' create a vlc player '''
    args = []
    if _isLinux:
        args.append('--no-xlib')
    Instance = vlc.Instance(args)
    player = Instance.media_player_new()

    # set where media player should render output
    video_widget_id = window['VIDEO'].Widget.winfo_id()
    if _isWindows:
        player.set_hwnd(video_widget_id)
    else:
        player.set_xwindow(video_widget_id)

    return player, Instance


def vlc_add_media(media, player, window, instance):
    media = instance.media_new(str(media))
    player.set_media(media)
    player.play()


def media_local(window):
    ''' get local video file '''
    filename = sg.PopupGetFile('Select media file')
    if filename is not None:
        window['INFO'].update(value=filename)
        window['PLAY'].update(image_filename=BUTTONS['PLAY_ON'])        

    return filename


def media_stream(window):
    ''' get streaming video from url '''
    try:
        url = sg.popup_get_text('Enter a url', default_text=DEFAULT_URL)
        video = pafy.new(url)
        best = video.getbest(preftype="mp4")
        info = "Channel: {} | Title: {} | Category: {}"
        window['INFO'].update(value = info.format(video.author, video.title, video.category))
        window['PLAY'].update(image_filename=BUTTONS['PLAY_ON'])
        return best.url
    except:
        return None

# ------ GUI ------------------------------------------------------------------------------------ #
def btn(key, image):
    ''' create player buttons '''
    return sg.Button(image_filename=image, border_width=0, key=key, button_color=('white', DEFAULT_BG_COLOR))


def gui():                     
    ''' create a gui instance '''
    rcmenu = ['&File', ['O&pen Local File', 'Open &YouTube Stream', '---', '&Play', '&Stop', '&Mute', '---', '&Exit']]
    layout = [[sg.Text('(Right-Click) Open a FILE or STREAM to begin', font=(sg.DEFAULT_FONT, 8), size=(70,1), key='INFO')],
              [sg.Image(filename=DEFAULT_IMG, size=VIDEO_SIZE, key='VIDEO')],
              [sg.ProgressBar(size=(48, 15), max_value=(100), bar_color=('#F95650', '#D8D8D8'), orientation='h', key='TIME')],
              [btn('REWIND', BUTTONS['REWIND']), btn('PAUSE', BUTTONS['PAUSE_OFF']),
               btn('PLAY', BUTTONS['PLAY_OFF']), btn('STOP', BUTTONS['STOP']),
               btn('FORWARD', BUTTONS['FORWARD']), btn('SOUND', BUTTONS['SOUND_ON'])]]
    
    window = sg.Window('VLC Video Player', layout, right_click_menu=rcmenu, finalize=True)
    
    # set window icon for windows only
    if _isWindows:
        window.set_icon(icon=ICON)

    return window


def main():
    ''' main event loop '''
    window  = gui()
    player, instance = vlc_player(window)

    while True:
        event, values = window.read(timeout=1000)
        window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())

        if event in(None, 'Exit'):
            player.audio_set_mute(False)
            break
        if event in ('STOP', 'Stop'):
            player.stop()
            window['PLAY'].update(image_filename=BUTTONS['PLAY_OFF'])        
        if event in ('PLAY', 'Play'):
            player.play()
            window['PLAY'].update(image_filename=BUTTONS['PLAY_ON'])
            window['PAUSE'].update(image_filename=BUTTONS['PAUSE_OFF'])
            window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())
        if event == 'PAUSE':
            window['PAUSE'].update(image_filename=BUTTONS['PAUSE_ON'] if player.is_playing() else BUTTONS['PAUSE_OFF'])
            window['PLAY'].update(image_filename=BUTTONS['PLAY_OFF'] if player.is_playing() else BUTTONS['PLAY_ON'])        
            player.pause()
        if event == 'REWIND':
            player.set_position(max(0, player.get_position() - 0.02))
        if event == 'FORWARD':
            player.set_position(min(1, player.get_position() + 0.02))        
        if event in ('SOUND', 'Mute'):
            window['SOUND'].update(image_filename=BUTTONS['SOUND_ON'] if player.audio_get_mute() else BUTTONS['SOUND_OFF'])
            player.audio_set_mute(not player.audio_get_mute())
        if event == 'Open YouTube Stream':
            media = media_stream(window)
            if media is not None:
                vlc_add_media(media, player, window, instance)
        if event == 'Open Local File':
            media = media_local(window)
            if media is not None:
                vlc_add_media(media, player, window, instance)

main()                