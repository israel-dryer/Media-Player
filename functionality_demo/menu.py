import PySimpleGUI as sg
sg.change_look_and_feel('Black')

btn_fmt = {'size':(15, 1), 'button_color': ('white','black')}

mb_file = sg.ButtonMenu('File', ['File' ,['Stream YouTube', 'Open Local File', 'Open Playlist', 'Exit']], **btn_fmt)
mb_controls = sg.ButtonMenu('Controls', ['Controls', ['Play', 'Pause', 'Stop', 'Mute']], **btn_fmt)
mb_library = sg.ButtonMenu('Library', ['Library', ['Edit Library']], **btn_fmt)
mb_playlist = sg.ButtonMenu('Playlist', [None, ['Create Playlist', 'Edit Playlist', 'Delete Playlist', 'Open Playlist']], **btn_fmt)
mb_about = sg.ButtonMenu('About', [None, ['About Me']], **btn_fmt)

layout = [[mb_file, mb_controls, mb_library, mb_playlist, mb_about]]

window = sg.Window('Menu App', layout=layout, grab_anywhere=True, keep_on_top=True, no_titlebar=True)

while True:
    event, values = window.read()
    if event is None or values[0] == 'Exit':
        break
    if event == 'File':
        print(values[event])
    else:
        print(event, values)