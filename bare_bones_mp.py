"""
    Bare Bones YouTube Player Demo with Playlist
    Author      :   Israel Dryer
    Modified    :   2019-10-28
"""
import PySimpleGUI as sg 
import vlc
sg.change_look_and_feel('DarkBlue')

layout = [[sg.Input(default_text='Add URL to Playlist: ', key='NEW'), sg.Submit()],
          [sg.Image('', size=(530, 300), key='VID_OUT')],
          [sg.Button('Play', size=(7, 1)), sg.Button('Pause', size=(7, 1)), 
           sg.Button('Stop', size=(7, 1)), sg.Button('Previous', size=(7, 1)), 
           sg.Button('Next', size=(7, 1)),
           sg.Text('Seconds remaining:', key='TIME', size=(15, 1))]]

window = sg.Window('Mini Player', layout, finalize=True)

playlist = ['https://www.youtube.com/watch?v=mqhxxeeTbu0', 'https://www.youtube.com/watch?v=9Hb2oMlRI0I']

def new_player(window):
    inst = vlc.Instance()
    list_player = inst.media_list_player_new()
    media_list = inst.media_list_new(playlist)
    list_player.set_media_list(media_list)
    player = list_player.get_media_player()
    player.set_hwnd(window['VID_OUT'].Widget.winfo_id())
    return player, list_player

player, list_player = new_player(window)

while True:
    event, values = window.read(timeout=100)

    length = round(player.get_length()/1000, 0)
    elapsed = round(player.get_position() * length, 0)

    if event is None:
        break
    if event == 'Play':
        list_player.play()
    if event == 'Pause':
        list_player.pause()
    if event == 'Stop':
        list_player.stop()
    if event == 'Next':
        list_player.next()
    if event == 'Previous':
        list_player.previous()
    if event == 'Submit':
        player.stop()
        playlist.insert(0, values['NEW'])
        player, list_player = new_player(window)

    window['TIME'].update(value = "Elapsed: {:,.0f} / {:,.0f}".format(elapsed, length))