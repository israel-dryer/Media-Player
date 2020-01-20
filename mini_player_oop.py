"""
    Mini VLC media player for local and online streaming media
    Author: Israel Dryer
    Modified: 2020-01-20
"""
import PySimpleGUI as sg
from sys import platform as PLATFORM
import vlc
import pafy


class MediaPlayer:
    """ The main media player class """

    def __init__(self, window):

        # the PySimpleGUI window; we'll direct output to this window
        self.window = window

        # Create a vlc instance for constructing media player objects
        self.instance = vlc.Instance()

        # A list for storing your media files
        self.media_list = self.instance.media_list_new([])

        # A player that handles media files in lists
        self.list_player = self.instance.media_list_player_new()

        # Connect the list_layer to the media_list
        self.list_player.set_media_list(self.media_list)

        # Create a player - this gives more fine-tuned control
        # over the object currently being played
        self.player = self.list_player.get_media_player()

        # Platform specific adjustments to the window handler
        if PLATFORM.startswith('linux'):
            self.player.set_xwindow(self.window['VID_OUT'].Widget.winfo_id())
        else:
            self.player.set_hwnd(self.window['VID_OUT'].Widget.winfo_id())

    def add_media(self):
        """ Add a new track to the list player with meta data
            if available """

        # open a popup window to ask user for media url
        url = sg.PopupGetFile('Browse for local media or enter URL:',
                              title='Load Media')

        # User did not provide any information
        if url is None:
            return
        # Attempt to get the video title from url, otherwise use filename
        try:
            vid = pafy.new(url)
            media = self.instance.media_new(vid.getbest().url)
            media.set_meta(0, vid.title)
        except:
            media = self.instance.media_new(url)
            media.set_meta(0, url.replace(r"\\", "/").split("/").pop())
        # add the media file to the media list and play if first item in list
        finally:
            self.media_list.add_media(media)
            if self.media_list.count() == 1:
                self.list_player.play()

    def get_track_info(self):
        """ Show the author, title, and elapsed time if video
            is loading and playing """

        # Strings to format for media display
        time_elapsed = "{:02d}:{:02d}".format(*divmod(self.player.get_time()//1000, 60))
        time_total = "{:02d}:{:02d}".format(*divmod(self.player.get_length()//1000, 60))

        # Check if player is playing and show info if it is
        if self.player.is_playing():
            self.window['INFO'].update("{}".format(self.player.get_media().get_meta(0)))
            self.window['TIME_ELAPSED'].update(time_elapsed)
            self.window['TIME'].update(self.player.get_position())
            self.window['TIME_TOTAL'].update(time_total)
        else:
            try:
                self.window['INFO'].update("{}".format(self.player.get_media().get_meta(0)))
            except:
                self.window['INFO'].update('LOAD media to Start')


class MediaWindow(sg.Window):
    """ The window used to output the media player content """

    def __init__(self, title, theme):

        # Change color theme of media player
        sg.change_look_and_feel(theme)

        # Create and set the window layout
        layout = [
            # Info bar for communicating messages to user
            [sg.Text('LOAD media to Start', size=(40, 1), justification='left',
                     font=(sg.DEFAULT_FONT, 10), key='INFO')],

            # This is where the media content will be displayed
            [sg.Image('images/default.png', size=(426, 240), key='VID_OUT')],

            # Media statistics and time slider bar
            [sg.Text('00:00', key='TIME_ELAPSED'),
             sg.Slider(range=(0, 1), enable_events=True, resolution=0.0001,
                       disable_number_display=True, background_color='#83D8F5',
                       orientation='h', key='TIME'),
             sg.Text('00:00', key='TIME_TOTAL')],

            # Media player buttons
            [self.create_button('previous'),
             self.create_button('play'),
             self.create_button('next'),
             self.create_button('pause'),
             self.create_button('stop'),
             self.create_button('media', button_color=('#000000','#7EE8F5'), focus=True)]]

        super().__init__(title, layout, element_justification='center', finalize=True)

        # Adjust the time & info text to be expandable
        self['TIME'].expand(expand_x=True)
        self['INFO'].expand(expand_x=True)

    @staticmethod
    def create_button(name, **kwargs):
        """ Helper function to quickly create buttons """
        return sg.Button(name, size=(7, 1), pad=(1, 1), key=name.upper(), **kwargs)


def main():
    """ The main program """
    win = MediaWindow('Mini Player', 'DarkBlue')
    mp = MediaPlayer(win)

    # Main event loop
    while True:
        event, values = win.read(timeout=1000) # Refresh minimum every second
        mp.get_track_info()

        if event is None: # user clicks exit button
            break
        if event == 'PLAY':
            mp.list_player.play()
        if event == 'PAUSE':
            mp.list_player.pause()
        if event == 'NEXT':
            mp.list_player.next()
        if event == 'PREVIOUS':
            mp.list_player.previous()
        if event == 'MEDIA':
            mp.add_media()
        if event == 'STOP':
            mp.player.stop()
            win['TIME_ELAPSED'].update('00:00')
        if event == 'TIME':
            mp.player.set_position(values['TIME'])
            time_elapsed = divmod(int(mp.player.get_length()*values['TIME'])//1000, 60)
            win['TIME_ELAPSED'].update("{:02d}:{:02d})".format(*time_elapsed))


if __name__ == '__main__':
    print('Starting program...')
    main()