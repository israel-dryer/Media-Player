"""
    Media Player for local and streaming online videos.

    Author:     Israel Dryer, israel.dryer@gmail.com
    Modified:   10/27/2019
"""
import PySimpleGUI as sg
import vlc
import pafy
import pickle
from os import listdir
from collections import namedtuple
from sys import platform as PLATFORM

# check operating system
_isMacOS   = PLATFORM.startswith('darwin')
_isWindows = PLATFORM.startswith('win')
_isLinux = PLATFORM.startswith('linux')

# ----------------------- MISC DEFAULT SETTINGS ---------------------------- #

DEFAULT_URL = 'https://www.youtube.com/watch?v=jE-SpRI3K5g'

WINDOW_SIZE = (1280, 720)
SCALE = 0.5
VIDEO_SIZE = tuple([x * SCALE for x in WINDOW_SIZE])

THEME = 'DarkBlue'
sg.change_look_and_feel(THEME)
DEFAULT_BG_COLOR = sg.LOOK_AND_FEEL_TABLE[THEME]['BACKGROUND']

# ------------------------------- IMAGES ----------------------------------- #

PATH = './images/'
BUTTON_PATH = PATH + 'button_images/win_white/'
BUTTONS = {img[:-4].upper(): BUTTON_PATH + img for img in listdir(BUTTON_PATH)}
DEFAULT_IMG = PATH + 'default.png'
ICON = PATH + 'player.ico'

# ---------------------------- VLC FUNCTIONS ------------------------------- #

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
# ---------------------------------------------------------------------------#
#                       ~~   MEDIA PLAYER GUI   ~~                           #
# ---------------------------------------------------------------------------#


# --------------------------- GUI FUNCTIONS ---------------------------------#

def play_video(window, player):
    player.play()
    window['PLAY'].update(image_filename=BUTTONS['PLAY_ON'])
    window['PAUSE'].update(image_filename=BUTTONS['PAUSE_OFF'])
    window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())


def stop_video(window, player):
    player.stop()
    window['PLAY'].update(image_filename=BUTTONS['PLAY_OFF'])  


def pause_video(window, player):
    window['PAUSE'].update(image_filename=BUTTONS['PAUSE_ON'] if player.is_playing() else BUTTONS['PAUSE_OFF'])
    window['PLAY'].update(image_filename=BUTTONS['PLAY_OFF'] if player.is_playing() else BUTTONS['PLAY_ON'])        
    player.pause()


def toggle_sound(window, player):
    window['SOUND'].update(image_filename=BUTTONS['SOUND_ON'] if player.audio_get_mute() else BUTTONS['SOUND_OFF'])
    player.audio_set_mute(not player.audio_get_mute())    


def play_local_video(window, player, instance):
    media = media_local(window)
    if media is not None:
        vlc_add_media(media, player, window, instance)


def play_youtube_video(window, player, instance):
    media = media_stream(window)
    if media is not None:
        vlc_add_media(media, player, window, instance)


def get_playlist():
    pass

def main():
    ''' main window event loop '''
    window  = gui()
    player, instance = vlc_player(window)

    while True:
        event, values = window.read(timeout=1000)
        window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())

        if event in(None, 'Exit'):
            player.audio_set_mute(False)
            break
        if event in ('STOP', 'Stop'):
            stop_video(window, player)
        if event in ('PLAY', 'Play'):
            play_video(window, player)
        if event in ('PAUSE', 'Pause'):
            pause_video(window, player)
        if event == 'REWIND':
            player.set_position(max(0, player.get_position() - 0.02))
        if event == 'FORWARD':
            player.set_position(min(1, player.get_position() + 0.02))        
        if event in ('SOUND', 'Mute'):
            toggle_sound(window, player)
        if event == 'Stream YouTube':
            play_youtube_video(window, player, instance)
        if event == 'Open Local File':
            play_local_video(window, player, instance)
        if event == 'Open Playlist':
            window.hide()
            pl_main_loop(window)

# ----------------------------- GUI LAYOUT --------------------------------- #

def btn(key, image):
    ''' create player buttons '''
    return sg.Button(image_filename=image, border_width=0, key=key, button_color=('white', DEFAULT_BG_COLOR))

def gui():                     
    ''' create a gui instance '''
    menu_layout = [['File', ['Stream YouTube', 'Open Local File', 'Open Playlist']],
                   ['Controls', ['Play', 'Pause', 'Stop', 'Mute']],
                   ['Library', ['Edit Library']],
                   ['Playlist', ['Create Playlist', 'Edit Playlist', 'Delete Playlist', 'Open Playlist']],
                   ['About']]

    main_layout = [
        [sg.Menu(menu_layout)],
        [sg.Text('Open a FILE, STREAM, or PLAYLIST to begin', font=(sg.DEFAULT_FONT, 8), size=(70,1), key='INFO')],
        [sg.Image(filename=DEFAULT_IMG, size=VIDEO_SIZE, key='VIDEO')],
        [sg.ProgressBar(size=(58, 15), auto_size_text=True, max_value=(100), bar_color=('#F95650', '#D8D8D8'), orientation='h', key='TIME')],
        [btn('REWIND', BUTTONS['REWIND']), btn('PAUSE', BUTTONS['PAUSE_OFF']), btn('PLAY', BUTTONS['PLAY_OFF']), 
         btn('STOP', BUTTONS['STOP']), btn('FORWARD', BUTTONS['FORWARD']), btn('SOUND', BUTTONS['SOUND_ON'])]]
    
    window = sg.Window('VLC Video Player', main_layout, finalize=True)
    
    # set window icon for windows only
    if _isWindows:
        window.set_icon(icon=ICON)

    return window

# ---------------------------------------------------------------------------#
#                           ~~   PLAYLIST GUI   ~~                           #
# ---------------------------------------------------------------------------#

Video = namedtuple("Video", "channel title url")

# -------------------- LOAD MEDIA LIBRARY AND PLAYLIST ----------------------#

with open('library.pkl', 'rb') as file:
    library = pickle.load(file)

with open('playlist.pkl', 'rb') as file:
    playlist = pickle.load(file)

for vid in library:
    print(vid.title)

# --------------------------- PLAYLIST FUNCTIONS ----------------------------#

def get_media_info(url):
    """ download meta data for video """
    video = pafy.new(url)
    return Video(channel=video.author, title=video.title, url=url)


def show_library(library, window, playlist):
    """ add playlist items from library """
    def create_layout():
        layout = [[sg.Text('Selected items will be added to the playlist.....\n', font=(sg.DEFAULT_FONT, 10))]]
        for i, vid in enumerate(library):
            layout.append([sg.Check('', pad=(0, 0)), 
                           sg.Input(vid.channel, pad=(0, 0), size=(20, 1), font=(sg.DEFAULT_FONT, 12), key=f'C{i}'), 
                           sg.Input(vid.title, pad=(0, 0), size=(60, 1), font=(sg.DEFAULT_FONT, 12), key=f'T{i}')])
        layout.append([sg.Text(' ')])
        layout.append([pl_btn('ok', 'OK')])            
        return layout 

    lib_window = sg.Window('Media Library', create_layout(), grab_anywhere=True)

    # set window icon for windows only
    if _isWindows:
        lib_window.set_icon(icon=ICON)

    lib_event, lib_values = lib_window.read()

    if lib_event == 'CANCEL':
        lib_window.close()
    if lib_event == 'OK':
        for key, val in lib_values.items():
            if val and isinstance(val, int):
                video = library[key].title
                playlist.append(video)
                pos = len(playlist)-1
                window['PLAYLIST'].update(values=playlist, set_to_index=pos)
        lib_window.close()


def move_up(window, values):
    """ move video track to an earlier position """
    try:
        # lookup index of selected track
        ix = window['PLAYLIST'].get_indexes()[0]
        # remove item from current position and move up        
        pos = max(ix-1, 0)
        item = playlist.pop(ix)
        playlist.insert(pos, item)
        window['PLAYLIST'].update(values=playlist, set_to_index=pos)            
    except:
        pass


def move_down(window, values):
    """ move video track to a later position """
    try:
        # lookup index of selected track
        ix = window['PLAYLIST'].get_indexes()[0]
        # remove item from current position and move down
        item = playlist.pop(ix)
        pos = min(ix + 1, len(playlist))
        playlist.insert(pos, item)
        window['PLAYLIST'].update(values=playlist, set_to_index=pos)     
    except:
        pass


def remove_video(window, values, library):
    """ remove a video from the playlist """
    try:
        ix = window['PLAYLIST'].get_indexes()[0]
        playlist.pop(ix)
        pos = min(len(playlist)-1, ix)
        window['PLAYLIST'].update(values=playlist, set_to_index=pos)
    except:
        pass


def add_video(window, values):
    """ add a video from the playlist and library """
    try:
        # insert after the currently select track
        pos = window['PLAYLIST'].get_indexes()[0] + 1
    except:
        # append to end of list
        pos = len(playlist)-1
    # user input url
    url = sg.popup_get_text(title='Add YouTube Video', message='Input a YouTube video url')
    if url is None:
        return
    # download video meta data
    video = get_media_info(url)
    # add video if not in library
    if video not in library:
        library.append(video)
    # add video to playlist and update window
    playlist.insert(pos, video.title)
    window['PLAYLIST'].update(values=playlist, set_to_index=pos)

def submit_playlist():
    """ save library and playlist """
    with open('library.pkl', 'wb') as f:
        pickle.dump(library, f)
    with open('playlist.pkl', 'wb') as f:
        pickle.dump(playlist, f)    
    sg.popup_ok('Playlist added to media player')  


# ------------------------- LIBRARY EDIT GUI ------------------------------- #

""" add library edit functionality here """

# --------------------------- PLAYLIST GUI LAYOUT -------------------------- #

def pl_btn(image, key): 
    """ create button with images for layout """
    filename = BUTTON_PATH + image + '.png'
    return sg.Button(image_filename=filename, button_color=('white', DEFAULT_BG_COLOR),
        border_width=0, pad=(1,1), key=key)


def create_window():
    col1 = [[pl_btn('plus', 'PLUS'), pl_btn('minus', 'MINUS'), pl_btn('up', 'UP'), pl_btn('down', 'DOWN')]]
    col2 = [[sg.Listbox(playlist, key='PLAYLIST', pad=(5, 0), font=(sg.DEFAULT_FONT, 12), size=(70, 10))]]

    layout = [[sg.Col(col1, pad=(0, 0))], 
              [sg.Col(col2, pad=(0, 10))], 
              [pl_btn('ok', 'OK'), pl_btn('cancel', 'CANCEL'), pl_btn('library','LIBRARY')]]

    window = sg.Window('Playlist Builder', layout, grab_anywhere=True, margins=(5, 5))
    return window

# --------------------------PLAYLIST MAIN EVENT LOOP ----------------------- #
def pl_main_loop(parent_window):
    pl_window = create_window()

    # set window icon for windows only
    if _isWindows:
        pl_window.set_icon(icon=ICON)

    while True:
        pl_event, pl_values = pl_window.read()
        if pl_event in (None, 'CANCEL'):
            parent_window.un_hide()
            pl_window.close()
            break
        if pl_event == 'PLUS':
            add_video(pl_window, pl_values)
        if pl_event == 'MINUS':
            remove_video(pl_window, pl_values, library)
        if pl_event == 'UP':
            move_up(pl_window, pl_values)
        if pl_event == 'DOWN':
            move_down(pl_window, pl_values)
        if pl_event == 'LIBRARY':
            show_library(library, pl_window, playlist)
        if pl_event == 'OK':
            submit_playlist()
            parent_window.un_hide()
            pl_window.close()
            break

# -------------------------------------------------------------------------- #

main()                