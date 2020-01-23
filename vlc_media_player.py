"""
    VLC media player for local and online streaming media
    Author: Israel Dryer
    Modified: 2020-01-23

"""
import vlc
import pafy
import PySimpleGUI as sg
from sys import platform as PLATFORM
from os import listdir

PATH = './Assets/'
BUTTON_DICT = {img[:-4].upper(): PATH + img for img in listdir(PATH)}
DEFAULT_IMG = PATH + 'background2.png'
ICON = PATH + 'player.ico'


class MediaPlayer:

    def __init__(self, size, scale=1.0, theme='DarkBlue'):
        """ Media player constructor """

        # Setup media player
        self.instance = vlc.Instance()
        self.list_player = self.instance.media_list_player_new()
        self.media_list = self.instance.media_list_new([])
        self.list_player.set_media_list(self.media_list)
        self.player = self.list_player.get_media_player()

        self.track_cnt = 0  # Count of tracks loaded into `media_list`
        self.track_num = 0  # Index of the track currently playing

        # Setup GUI window for output of media
        self.theme = theme  # This can be changed, but I'd stick with a dark theme
        self.default_bg_color = sg.LOOK_AND_FEEL_TABLE[self.theme]['BACKGROUND']
        self.window_size = size  # The size of the GUI window
        self.player_size = [x*scale for x in size]  # The size of the media output window
        self.window = self.create_window()
        self.check_platform()  # Window handler adj for Linux/Windows/MacOS

        # Unmute the volume if muted
        if self.player.audio_get_mute():
            self.toggle_mute()

    def button(self, key, image, **kwargs):
        """ Create media player button """
        return sg.Button(image_filename=image, border_width=0, pad=(0, 0), key=key,
                         button_color=('white', self.default_bg_color))

    def create_window(self):
        """ Create GUI instance """
        sg.change_look_and_feel(self.theme)

        # Column layout for media player button controls
        col1 = [[self.button('SKIP PREVIOUS', BUTTON_DICT['START']),
                 self.button('PAUSE', BUTTON_DICT['PAUSE_OFF']),
                 self.button('PLAY', BUTTON_DICT['PLAY_OFF']),
                 self.button('STOP', BUTTON_DICT['STOP']),
                 self.button('SKIP NEXT', BUTTON_DICT['END']),
                 self.button('SOUND', BUTTON_DICT['SOUND_ON']),
                 self.button('PLAYLIST', BUTTON_DICT['PLAYLIST']),
                 self.button('PLUS', BUTTON_DICT['PLUS'])]]

        # Column layout for media info and instructions
        col2 = [[sg.Text('Open a FILE, STREAM, or PLAYLIST to begin',
                         size=(45, 3), font=(sg.DEFAULT_FONT, 8), pad=(0, 5), key='INFO')]]

        # Main GUI layout
        main_layout = [
            # Media output element -- this is the video output element
            [sg.Image(filename=DEFAULT_IMG, pad=(0, 5), size=self.player_size, key='VID_OUT')],

            # Element for tracking elapsed time
            [sg.Text('00:00', key='TIME_ELAPSED'),

             # This slide can be used to adjust the playback positon of the video
             sg.Slider(range=(0, 1), enable_events=True, resolution=0.0001, disable_number_display=True,
                       background_color='#83D8F5', orientation='h', key='TIME'),

             # Elements for tracking media length and track counts
             sg.Text('00:00', key='TIME_TOTAL'),
             sg.Text('          ', key='TRACKS')],

            # Button and media information layout (created above)
            [sg.Column(col1), sg.Column(col2)]]

        # Create a PySimpleGUI window from the specified parameters
        window = sg.Window('VLC Media Player', main_layout, element_justification='center', icon=ICON, finalize=True)

        # Expand the time element so that the row elements are positioned correctly
        window['TIME'].expand(expand_x=True)
        return window

    def check_platform(self):
        """ Platform specific adjustments for window handler """
        if PLATFORM.startswith('linux'):
            self.player.set_xwindow(self.window['VID_OUT'].Widget.winfo_id())
        else:
            self.player.set_hwnd(self.window['VID_OUT'].Widget.winfo_id())

    def add_media(self, track=None):
        """ Add new track to list player with meta data if available """
        if track is None:
            return  # User did not provide any information

        try:  # Assume this is an online url and not a file path
            vid = pafy.new(track)  # Create pafy media object
            media = self.instance.media_new(vid.getbest().url)  # Get REAL YouTube url
            # Set meta data for media if available
            media.set_meta(0, vid.title)
            media.set_meta(1, vid.author)

        except:  # This is a file path and not an online url
            media = self.instance.media_new(track)
            media.set_meta(0, track.replace('\\', '/').split('/').pop())  # filename
            media.set_meta(1, 'Local Media')  # Default author value for local media

        finally:
            media.set_meta(10, track)  # Url if online media else use filename
            self.media_list.add_media(media)
            self.track_cnt = self.media_list.count()

            # Update infobar with added track
            self.window['INFO'].update(f'Loaded: {media.get_meta(0)}')
            self.window.read(1)  # refresh the screen

            # Update the track counter
            if self.track_cnt == 1:
                self.track_num = 1
                self.list_player.play()

    def get_meta(self, meta_type):
        """ Retrieve saved meta data from tracks in media list """
        media = self.player.get_media()
        return media.get_meta(meta_type)

    def get_track_info(self):
        """ Show author, title, and elasped time if video is loaded and playing """
        time_elapsed = "{:02d}:{:02d}".format(*divmod(self.player.get_time() // 1000, 60))
        time_total = "{:02d}:{:02d}".format(*divmod(self.player.get_length() // 1000, 60))
        if self.player.is_playing():
            message = "{}\n{}".format(self.get_meta(1).upper(), self.get_meta(0))
            self.window['INFO'].update(message)
            self.window['TIME_ELAPSED'].update(time_elapsed)
            self.window['TIME'].update(self.player.get_position())
            self.window['TIME_TOTAL'].update(time_total)
            self.window['TRACKS'].update('{} of {}'.format(self.track_num, self.track_cnt))
        elif self.media_list.count() == 0:
            self.window['INFO'].update('Open a FILE, STREAM, or PLAYLIST to begin')
        else:
            self.window['INFO'].update('Press PLAY to Start')

    def play(self):
        """ Called when the play button is pressed """
        self.list_player.play()
        self.window['PLAY'].update(image_filename=BUTTON_DICT['PLAY_ON'])
        self.window['PAUSE'].update(image_filename=BUTTON_DICT['PAUSE_OFF'])

    def stop(self):
        """ Called when the stop button is pressed """
        self.player.stop()
        self.window['PLAY'].update(image_filename=BUTTON_DICT['PLAY_OFF'])
        self.window['PAUSE'].update(image_filename=BUTTON_DICT['PAUSE_OFF'])
        self.window['TIME'].update(value=0)
        self.window['TIME_ELAPSED'].update('00:00')

    def pause(self):
        """ Called when the pause button is pressed """
        self.window['PAUSE'].update(
            image_filename=BUTTON_DICT['PAUSE_ON'] if self.player.is_playing() else BUTTON_DICT['PAUSE_OFF'])
        self.window['PLAY'].update(
            image_filename=BUTTON_DICT['PLAY_OFF'] if self.player.is_playing() else BUTTON_DICT['PLAY_ON'])
        self.player.pause()

    def skip_next(self):
        """ Called when the skip next button is pressed """
        self.list_player.next()
        self.reset_pause_play()
        if not self.track_cnt == self.track_num:
            self.track_num += 1

    def skip_previous(self):
        """ Called when the skip previous button is pressed """
        self.list_player.previous()
        self.reset_pause_play()
        if not self.track_num == 1:
            self.track_num -= 1

    def reset_pause_play(self):
        """ Reset pause play buttons after skipping tracks """
        self.window['PAUSE'].update(image_filename=BUTTON_DICT['PAUSE_OFF'])
        self.window['PLAY'].update(image_filename=BUTTON_DICT['PLAY_ON'])

    def toggle_mute(self):
        """ Called when the sound button is pressed """
        self.window['SOUND'].update(
            image_filename=BUTTON_DICT['SOUND_ON'] if self.player.audio_get_mute() else BUTTON_DICT['SOUND_OFF'])
        self.player.audio_set_mute(not self.player.audio_get_mute())

    def load_single_track(self):
        """ Open a popup to request url or filepath for single track """
        track = sg.PopupGetFile('Browse for local media or enter URL:',
                                title='Load Media')
        if track is None:
            return
        else:
            self.window['INFO'].update('Loading media...')
            self.window.read(1)
            self.add_media(track)
        if self.media_list.count() > 0:
            self.play()

    def load_playlist_from_file(self):
        """ Open text file and load to new media list. Assumes `playlist.txt` is in root directory """

        # Read contents of playlist file
        with open('./playlist.txt', 'r') as f:
            try:
                playlist = f.read().splitlines()
            except IOError:
                sg.popup_error('There was an error opening the file. Please make sure `playlist.txt` is in\
                the same path as the media player executable', title='Playlist Error')
                return

        # Send message to window and update
        self.window['INFO'].update('Loading playlist...')
        self.window.read(1)

        # Add each track to the playlist if a valid url or file path
        for track in playlist:
            if track.strip():
                self.add_media(track.replace('\\', '/'))

                # Play this track if player not playing (allows for faster perceived startup)
                if not self.player.is_playing:
                    self.play()

        # Increment the track counter
        self.track_cnt = self.media_list.count()
        self.track_num = 1


def main():
    """ The main program function """

    # Create the media player
    mp = MediaPlayer(size=(1920, 1080), scale=0.5)

    # Main event loop
    while True:
        event, values = mp.window.read(timeout=1000)
        mp.get_track_info()
        if event in (None, 'Exit'):
            break
        if event == 'PLAY':
            mp.play()
        if event == 'PAUSE':
            mp.pause()
        if event == 'SKIP NEXT':
            mp.skip_next()
        if event == 'SKIP PREVIOUS':
            mp.skip_previous()
        if event == 'STOP':
            mp.stop()
        if event == 'SOUND':
            mp.toggle_mute()
        if event == 'TIME':
            mp.player.set_position(values['TIME'])
        if event == 'PLUS':
            mp.load_single_track()
        if event == 'PLAYLIST':
            mp.load_playlist_from_file()


if __name__ == '__main__':
    main()