import os
import logging
import io
import PySimpleGUI as sg
from PIL import Image
import PIL

from indexr.utils import load_creds_to_environ
from indexr.db.query_manipulation import TableQueries

load_creds_to_environ()

test_path = "/Users/jayglickman/Library/CloudStorage/Dropbox/Pictures/Costume Album/2010_Inigo Montoya_1.jpg"
fsize = os.path.getsize(test_path)
print("fsize:", fsize)
with Image.open(test_path) as img:  # PIL solution
    print("exif", img.getexif)
    bio = io.BytesIO()
    cur_width, cur_height = img.size
    new_width, new_height = 200, 200
    scale = min(new_height/cur_height, new_width/cur_width)
    img = img.resize((int(cur_width*scale), int(cur_height*scale)))
    
    img.save(bio, format="PNG")
    print("type type", type(img))


def load_image_from_path(file_path, resize_x=200, resize_y=200):
    print("file path", file_path)
    with Image.open(file_path) as img:  # PIL solution
        logging.debug("exif", img.getexif)
        bio = io.BytesIO()
        cur_width, cur_height = img.size
        new_width, new_height = resize_x, resize_y
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)))
        img.save(bio, format="PNG")
        return bio


layout = [
    [sg.Text("What's your name?")],
    [sg.Input(key="-INPUT-")],
    [sg.Text(size=(40, 1), key="-OUTPUT-")],
    [sg.Button("Random Image"), sg.Button("Quit")],
    [sg.Image(key="-PREVIEW-", size=(200, 200))]
]

# Create the window
window = sg.Window("Window Title", layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == "Quit":
        break
    # Output a message to the window
    elif event == "Random Image":
        query_class = TableQueries()
        random_row = query_class.get_random_image_ref()
        print("random row file--->", random_row.get("file"))
        preview_img = load_image_from_path(random_row.get("file"))
        print("type-->", type(preview_img))
        print("image--->", preview_img)
        layout = [
            [sg.Text("What's your name?")],
            [sg.Input(key="-INPUT-")],
            [sg.Text(size=(40, 1), key="-OUTPUT-")],
            [sg.Button("Random Image"), sg.Button("Quit")],
            [sg.Image(preview_img, size=(200, 200), key='-IMAGE-')],
        ]
        window["-PREVIEW-"].update(
            data=preview_img.getvalue()
        )
    window["-OUTPUT-"].update(
        "Hello " + values["-INPUT-"] + "! Thanks for trying PySimpleGUI"
    )

# Finish up by removing from the screen
window.close()
