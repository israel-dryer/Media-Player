"""
    YouTube playlist builder
    Author      :   Israel Dryer, israel.dryer@gmail.com
    Modified    :   2019-10-27 
"""
import PySimpleGUI as sg
import pafy
from collections import namedtuple
import pickle

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
        layout = [[sg.Text('Click all that you wish to add to the playlist.....\n', font=(sg.DEFAULT_FONT, 12, 'bold'))]]
        for vid in library:
            layout.append([sg.Checkbox(vid.title, tooltip=vid.channel, font=(sg.DEFAULT_FONT, 12), pad=(0, 0))])
        layout.append([sg.Text(' ')])
        layout.append([btn('ok', 'OK'), btn('cancel', 'CANCEL')])            
        return layout 

    lib_window = sg.Window('Media Library', create_layout())
    lib_event, lib_values = lib_window.read()

    if lib_event == 'CANCEL':
        lib_window.close()
    if lib_event == 'OK':
        for key, val in lib_values.items():
            if val:
                video = library[key].title
                playlist.append(video)
                pos = len(playlist)-1
                window['PLAYLIST'].update(values=playlist, set_to_index=pos)
        lib_window.close()


def move_up(window, values):
    """ move video track to an earlier position """
    try:
        # lookup index of selected track
        ix = playlist.index(values['PLAYLIST'].pop())
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
        pos = min(ix + 1, len(playlist)-1)
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
    url = sg.popup_get_text('YouTube URL:')
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
    filename = './images/button_images/' + image + '.png'
    return sg.Button(image_filename=filename, button_color=('white', sg.DEFAULT_BACKGROUND_COLOR), 
        border_width=0, pad=(1,1), key=key)


def create_window():
    col1 = [[btn('plus2', 'PLUS'), btn('minus2', 'MINUS'), btn('up2', 'UP'), btn('down2', 'DOWN'), 
             btn('ok', 'OK'), btn('cancel', 'CANCEL'), btn('library','LIBRARY')]]
    col2 = [[sg.Listbox(playlist, key='PLAYLIST', pad=(5, 0), font=(sg.DEFAULT_FONT, 12), size=(70, 10))]]

    layout = [[sg.Col(col1, pad=(0, 0))], [sg.Col(col2, pad=(0, 10))]]

    window = sg.Window('Media Player :: Build Playlist', layout, margins=(1, 1))
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
