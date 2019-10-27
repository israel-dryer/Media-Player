"""
    YouTube playlist builder
    Author      :   Israel Dryer, israel.dryer@gmail.com
    Modified    :   2019-10-27 
"""
import PySimpleGUI as sg
import pafy
from collections import namedtuple
import pickle

THEME = 'DarkBlue'
sg.change_look_and_feel(THEME)
DEFAULT_BG_COLOR = sg.LOOK_AND_FEEL_TABLE[THEME]['BACKGROUND']
print(DEFAULT_BG_COLOR)
IMG_PATH = './images/button_images/square_white/'

Video = namedtuple("Video", "channel title url")

# ----- LOAD MEDIA LIBRARY AND PLAYLIST --------------------------------------#
with open('library.pkl', 'rb') as file:
    library = pickle.load(file)

with open('playlist.pkl', 'rb') as file:
    playlist = pickle.load(file)

for vid in library:
    print(vid.title)

# ----- PLAYLIST FUNCTIONS ---------------------------------------------------#
def get_media_info(url):
    """ download meta data for video """
    video = pafy.new(url)
    return Video(channel=video.author, title=video.title, url=url)


def show_library(library, window, playlist):
    """ add playlist item from library """
    def create_layout():
        layout = [[sg.Text('Selected items will be added to the playlist.....\n', font=(sg.DEFAULT_FONT, 10))]]
        for i, vid in enumerate(library):
            #layout.append([sg.Checkbox(vid.title, tooltip=vid.channel, font=(sg.DEFAULT_FONT, 12), pad=(0, 0))])
            layout.append([sg.Check('', pad=(0, 0)), 
                           sg.Input(vid.channel, pad=(0, 0), size=(20, 1), font=(sg.DEFAULT_FONT, 12), key=f'C{i}'), 
                           sg.Input(vid.title, pad=(0, 0), size=(60, 1), font=(sg.DEFAULT_FONT, 12), key=f'T{i}')])
        layout.append([sg.Text(' ')])
        layout.append([btn('ok', 'OK')])            
        return layout 

    lib_window = sg.Window('Media Library', create_layout(), grab_anywhere=True)
    lib_event, lib_values = lib_window.read()

    if lib_event == 'CANCEL':
        lib_window.close()
    if lib_event == 'OK':
        print(lib_values)
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


# ----- PLAYLIST GUI -------------------------------------------------------- #
def btn(image, key): 
    """ create button with images for layout """
    filename = IMG_PATH + image + '.png'
    return sg.Button(image_filename=filename, button_color=('white', DEFAULT_BG_COLOR),
        border_width=0, pad=(1,1), key=key)


def create_window():
    col1 = [[btn('plus', 'PLUS'), btn('minus', 'MINUS'), btn('up', 'UP'), btn('down', 'DOWN'), 
             btn('library','LIBRARY'), btn('ok', 'OK'), btn('cancel', 'CANCEL')]]
    col2 = [[sg.Listbox(playlist, key='PLAYLIST', pad=(5, 0), font=(sg.DEFAULT_FONT, 12), size=(70, 10))]]

    layout = [[sg.Col(col1, pad=(0, 0))], [sg.Col(col2, pad=(0, 10))]]

    window = sg.Window('Media Player :: Build Playlist', layout, grab_anywhere=True, margins=(5, 5))
    return window


# ----- MAIN EVENT LOOP ----------------------------------------------------- #
window = create_window()

while True:
    event, values = window.read()
    if event in (None, 'CANCEL'):
        break
    if event == 'PLUS':
        add_video(window, values)
    if event == 'MINUS':
        remove_video(window, values, library)
    if event == 'UP':
        move_up(window, values)
    if event == 'DOWN':
        move_down(window, values)
    if event == 'LIBRARY':
        show_library(library, window, playlist)
    if event == 'Submit':
        sg.popup_ok('Playlist added to media player')       
        break

# ----- SAVE LIBRARY AND PLAYLIST ------------------------------------------- #
with open('library.pkl', 'wb') as f:
    pickle.dump(library, f)

with open('playlist.pkl', 'wb') as f:
    pickle.dump(playlist, f)
