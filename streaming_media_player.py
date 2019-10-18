import PySimpleGUI as sg 
import pafy
import vlc
import requests

theme = 'SystemDefault'
sg.change_look_and_feel(theme)
bg_color = sg.LOOK_AND_FEEL_TABLE[theme]['BACKGROUND']

# https://en.wikipedia.org/wiki/The_Dark_Side_of_the_Moon
# https://www.sketchappsources.com/free-source/7-desktop-music-player.html
# https://icons8.com/icon/pack/media-controls/ios-filled
# pip install --upgrade youtube-dl
# https://get.videolan.org/vlc/3.0.8/win64/vlc-3.0.8-win64.exe

# ------ VLC PLAYER ----------------------------------------------------------------------------- #
url = 'https://www.youtube.com/watch?v=cpbbuaIA3Ds'
media = pafy.new(url)
audio = media.getbestaudio()
playurl = audio.url 

Instance = vlc.Instance()
player = Instance.media_player_new()
Media = Instance.media_new(playurl)
player.set_media(Media)

# ------ GUI LAYOUT ----------------------------------------------------------------------------- #
image_files = ['forward', 'pause', 'play', 'rewind', 'stop']
images = {image: 'images/small/' + image + '.png' for image in image_files}
images['album'] = sg.Image(data=requests.get('https://www.sageaudio.com/blog/wp-content/uploads/2014/04/album-art-300x300.png').content)

btn = {'border_width': 0, 'button_color': ('white', bg_color)}

col1 = [[images['album']]] # album art
col2 = [[sg.Text('Pink Floyd', font=('Arial Black', 22), pad=((10, 5), (40, 5)), size=(16, 1), key='ARTIST')],
        [sg.Text('The Dark Side of the Moon', font=('Arial', 12, 'bold'), pad=(10, 5), key='ALBUM')],
        [sg.Text('Money', font=('Arial', 12), pad=((10, 5), (5, 40)), key='SONG')],
        [sg.Button(image_filename='./images/rewind.png', **btn, key='REWIND'), 
         sg.Button(image_filename='./images/stop.png', **btn, key='PLAY'), 
         sg.Button(image_filename='./images/fast_forward.png', **btn, key='FF'),
         sg.Button(image_filename='./images/repeat_off.png', **btn, key='REPEAT'), 
         sg.Button(image_filename='./images/shuffle_off.png', **btn, key='SHUFFLE'), 
         sg.Button(image_filename='./images/sound_on.png', **btn, key='SOUND')], 
        [sg.ProgressBar(max_value=100, pad=((5, 5), (20, 5)), size=(25, 30), style='winnative', bar_color=('#F95650', '#D8D8D8'), key='TIME')]]

player_layout = [[sg.Column(col1, justification='left', key='LEFT'), sg.Column(col2, key='RIGHT')]]

window = sg.Window('Music Player', player_layout, margins=(5, 10), finalize=True)
window['LEFT'].expand(expand_y=True)
window['RIGHT'].expand(expand_y=True)

pause = True
repeat = False
shuffle = False
sound = False

while True:
    event, values = window.read(timeout=100)
    if event is None:
        break
    if event == 'PLAY':
        if pause:
            pause = False
            window['PLAY'].update(image_filename='./images/play.png')
            window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())
            player.play()
        else:
            pause = True 
            window['PLAY'].update(image_filename='./images/pause_red.png')
            window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())
            player.pause()
    if event == 'SOUND':
        if sound:
            sound = False
            window['SOUND'].update(image_filename='./images/sound_on.png')
        else:
            sound = True 
            window['SOUND'].update(image_filename='./images/sound_off.png')
    if event == 'REPEAT':
        if repeat:
            repeat = False
            window['REPEAT'].update(image_filename='./images/repeat_off.png')
        else:
            repeat = True 
            window['REPEAT'].update(image_filename='./images/repeat_on.png')    
    if event == 'SHUFFLE':
        if shuffle:
            shuffle = False
            window['SHUFFLE'].update(image_filename='./images/shuffle_off.png')
        else:
            shuffle = True 
            window['SHUFFLE'].update(image_filename='./images/shuffle_on.png')    
    else:
        window['TIME'].update_bar(current_count=player.get_time(), max=player.get_length())



