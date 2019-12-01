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

PATH = './images/'
BUTTON_PATH = PATH + 'button_images/win_white/'
BUTTON_DICT = {img[:-4].upper(): BUTTON_PATH + img for img in listdir(BUTTON_PATH)}
DEFAULT_IMG = PATH + 'default.png'
ICON = PATH + 'player.ico'

class MediaPlayer:

    def __init__(self, size, scale=0.5, theme='DarkBlue'):
        self.theme = theme
        self.default_bg_color = sg.LOOK_AND_FEEL_TABLE[self.theme]['BACKGROUND']
        self.window_size = size
        self.player_size = tuple([x * scale for x in size])
        self.instance = vlc.Instance()
        self.list_player = self.instance.media_list_player_new()
        self.media_list = self.instance.media_list_new([])
        self.list_player.set_media_list(self.media_list)
        self.player = self.list_player.get_media_player()
        self.track_cnt = 0
        self.track_num = 0
        self.menu = [
            ['File', ['Load &Media', 'Load &Playlist', '---', 'Exit']],
            ['Controls', ['Play', 'Pause', 'Stop','---','Skip Next', 'Skip Previous']],
            ['Playlist', ['Active Playlist', [], '---', 'Save New Playlist', 'Create from File', 'Edit Active Playlist']],
            ['Library', ['Edit Library']], ['About']]

        self.window = self.create_window()
        self.__adjust_for_platform()


    def __button(self, key, image):
        ''' create player buttons '''
        return sg.Button(image_filename=image, border_width=0, pad=(0, 0), key=key, button_color=('white', self.default_bg_color))            


    def create_window(self):
        ''' create a gui instance '''
        sg.change_look_and_feel(self.theme)
        col1 = [[self.__button('SKIP PREVIOUS', BUTTON_DICT['START']), 
                 self.__button('PAUSE', BUTTON_DICT['PAUSE_OFF']), 
                 self.__button('PLAY', BUTTON_DICT['PLAY_OFF']), 
                 self.__button('STOP', BUTTON_DICT['STOP']), 
                 self.__button('SKIP NEXT', BUTTON_DICT['END']), 
                 self.__button('SOUND', BUTTON_DICT['SOUND_ON'])]]

        col2 = [[sg.Text('Open a FILE, STREAM, or PLAYLIST to begin', 
                         size=(45, 3), font=(sg.DEFAULT_FONT, 8), pad=(0, 5), key='INFO')]]

        main_layout = [
            [sg.Menu(self.menu, key='MENU')],
            [sg.Image(filename=DEFAULT_IMG, pad=(0, 5), size=self.player_size, key='VID_OUT')],
            [sg.Text('00:00', key='TIME_ELAPSED'), 
             sg.Slider(range=(0, 1), enable_events=True, resolution=0.0001, disable_number_display=True, 
                       background_color='#83D8F5', orientation='h', key='TIME'),
             sg.Text('00:00', key='TIME_TOTAL'),
             sg.Text('          ', key='TRACKS')], 
            [sg.Column(col1), sg.Column(col2)]]
        
        window = sg.Window('VLC Media Player', main_layout, element_justification='center', finalize=True)
        window['TIME'].expand(expand_x=True)
        return window


    def __adjust_for_platform(self):
        # platform specific adjustments for window handler
        if PLATFORM.startswith('linux'):
            self.player.set_xwindow(self.window['VID_OUT'].Widget.winfo_id())
        else:
            self.player.set_hwnd(self.window['VID_OUT'].Widget.winfo_id())


    def add_media(self):
        """ add new track to list player with meta data if available """
        url = sg.PopupGetFile('Browse for local media or enter URL:', title='Load Media')
        if url is None:
            return
        try:
            vid = pafy.new(url)
            media = instance.media_new(vid.getbest().url)
            media.set_meta(0, vid.title)
            media.set_meta(1, vid.author)
            playlist_menu_add_track(vid.title, window)
        except:
            media = self.instance.media_new(url)
            media.set_meta(0, url.replace('\\','/').split('/').pop()) # filename
            media.set_meta(1, 'Local Media')
            self.playlist_menu_add_track('Local Media')
        finally:
            media.set_meta(10, url)
            self.media_list.add_media(media)
            self.track_cnt = self.media_list.count()
            if self.track_cnt == 1:
                self.track_num = 1
                self.list_player.play()


    def track_meta(self, meta_type):
        """ retrieve saved meta data from tracks in media list """
        media = self.player.get_media()
        return media.get_meta(meta_type)


    def trunc(self, string, chars):
        """ truncate string to a set number of characters """
        if len(string) > chars:
            return string[:chars] + "..."
        else:
            return string


    def track_info(self):
        """ show author, title, and elasped time if video is loaded and playing """
        time_elapsed = "{:02d}:{:02d}".format(*divmod(self.player.get_time()//1000, 60))
        time_total = "{:02d}:{:02d}".format(*divmod(self.player.get_length()//1000, 60))
        if self.player.is_playing():
            message = "{}\n{}".format(self.track_meta(1).upper(), self.track_meta(0))
            self.window['INFO'].update(message)
            self.window['TIME_ELAPSED'].update(time_elapsed)
            self.window['TIME'].update(self.player.get_position())
            self.window['TIME_TOTAL'].update(time_total)
            self.window['TRACKS'].update('{} of {}'.format(self.track_num, self.track_cnt))
        elif self.media_list.count() == 0:
            self.window['INFO'].update('Open a FILE, STREAM, or PLAYLIST to begin')
        else:
            self.window['INFO'].update('Press PLAY to Start')


    def play_video(self):
        self.list_player.play()
        self.window['PLAY'].update(image_filename=BUTTON_DICT['PLAY_ON'])
        self.window['PAUSE'].update(image_filename=BUTTON_DICT['PAUSE_OFF'])


    def stop_video(self):
        self.player.stop()
        self.window['PLAY'].update(image_filename=BUTTON_DICT['PLAY_OFF'])  
        self.window['PAUSE'].update(image_filename=BUTTON_DICT['PAUSE_OFF'])
        self.window['TIME'].update(value=0)
        self.window['TIME_ELAPSED'].update('00:00')


    def pause_video(self):
        self.window['PAUSE'].update(image_filename=BUTTON_DICT['PAUSE_ON'] if self.player.is_playing() else BUTTON_DICT['PAUSE_OFF'])
        self.window['PLAY'].update(image_filename=BUTTON_DICT['PLAY_OFF'] if self.player.is_playing() else BUTTON_DICT['PLAY_ON'])        
        self.player.pause()


    def skip_next(self):
        if not self.track_cnt == self.track_num:
            self.track_num +=1
        self.list_player.next()


    def skip_previous(self):
        if not self.track_num == 1:
            self.track_num -= 1
        self.list_player.previous()


    def toggle_sound(self):
        self.window['SOUND'].update(image_filename=BUTTON_DICT['SOUND_ON'] if self.player.audio_get_mute() else BUTTON_DICT['SOUND_OFF'])
        self.player.audio_set_mute(not self.player.audio_get_mute())    


    def playlist_create_from_file(self):
        """ open text file and load to new media list """
        filename = sg.popup_get_file('navigate to playlist', title='Create New Playlist', no_window=True)
        if filename is not None:
            with open(filename, 'r') as f:
                self.media_list = self.instance.media_list_new([])
                try:
                    playlist = f.read().splitlines()
                except:
                    sg.popup_error('Not able to create playlist from selected file.', title='Playlist Error')
                    return

            for url in playlist:
                try:
                    vid = pafy.new(url)
                    media = self.instance.media_new(vid.getbest().url)
                    media.set_meta(0, vid.title)
                    media.set_meta(1, vid.author)
                    self.playlist_menu_add_track(vid.title)
                except:
                    media = self.instance.media_new(url)
                    media.set_meta(0, url.replace('\\','/').split('/').pop()) # filename
                    media.set_meta(1, 'Local Media')
                    self.playlist_menu_add_track('Local Media')
                finally:
                    media.set_meta(10, url)
                    self.media_list.add_media(media)
            
            self.window['MENU'].update(menu_definition=self.menu)
            self.track_cnt = self.media_list.count()
            self.list_player.set_media_list(self.media_list)
            self.track_num = 1                
            self.list_player.play()


    def playlist_menu_add_track(self, name):
        trackmenu = [f'Delete::{name}', '---', f'Move Up::{name}', f'Move Down::{name}']
        self.menu[2][1][1].extend([name, trackmenu])        


if __name__ == '__main__':
    mp = MediaPlayer(size=(1280, 720))
    while True:
        event, values = mp.window.read(timeout=1000)
        mp.track_info()
        if event in (None, 'Exit'):
            break
        if event in ('PLAY', 'Play'):
            mp.play_video()
        if event in ('PAUSE', 'Pause'):
            mp.pause_video()
        if event in ('SKIP NEXT', 'Skip Next'):
            mp.skip_next()
        if event in ('SKIP PREVIOUS', 'Skip Previous'):
            mp.skip_previous()
        if event in ('STOP', 'Stop'):
            mp.stop_video()
        if event == 'SOUND':
            mp.toggle_sound()
        if event == 'TIME':
            mp.player.set_position(values['TIME'])
        if event == 'Load Media':
            mp.add_media()
        if event == 'Create from File':
            mp.playlist_create_from_file()
        else:
            print(event, values)