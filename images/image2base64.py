import PySimpleGUI as sg
import base64 
import os

destination = 'output.py'
source = sg.popup_get_folder('Source folder will be encoded and results saved to {}'.format(destination), title='Base64 Encoder')

if source is None:
    sg.popup_cancel('Cancelled - No source folder chosen.', title='Base64 Encoder')
else:
    files = [file for file in os.listdir(source) if file[-3:] in('png', 'ico', 'gif')]
    with open(destination, 'w') as outfile:
        for file in files:
            with open(source + '/' + file, 'rb') as imgfile:
                data = imgfile.read()
                img = base64.b64encode(data) 
                outfile.write("\n{} = {}".format(file[:-4], img))
    sg.popup('Completed. Encoded {:,d} files.'.format(len(files)))