import logging
import io
import PySimpleGUI as sg
from PIL import Image
import subprocess
import PIL

from indexr.utils import load_creds_to_environ, split_path_and_file
from indexr.db.query_manipulation import TableQueries

load_creds_to_environ()

PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT = 400, 400

# test_path = "/Users/jayglickman/Library/CloudStorage/Dropbox/Pictures/Costume Album/2010_Inigo Montoya_1.jpg"
# fsize = os.path.getsize(test_path)
# print("fsize:", fsize)
# with Image.open(test_path) as img:  # PIL solution
#     print("exif", img.getexif)
#     bio = io.BytesIO()
#     cur_width, cur_height = img.size
#     new_width, new_height = 200, 200
#     scale = min(new_height/cur_height, new_width/cur_width)
#     img = img.resize((int(cur_width*scale), int(cur_height*scale)))
    
#     img.save(bio, format="PNG")
#     print("type type", type(img))


def load_image_from_path(file_path, resize_x=PREVIEW_IMG_WIDTH, resize_y=PREVIEW_IMG_HEIGHT):
    print("file path", file_path)
    try:
        with Image.open(file_path) as img:  # PIL solution
            logging.debug("exif", img.getexif)
            bio = io.BytesIO()
            cur_width, cur_height = img.size
            new_width, new_height = resize_x, resize_y
            scale = min(new_height/cur_height, new_width/cur_width)
            img = img.resize((int(cur_width*scale), int(cur_height*scale)))
            img.save(bio, format="PNG")
            return bio
    except Exception as e:
        logging.warning(f"load_image_from_path unable to load image {file_path}: {e}")
        # return default image
        image = Image.new('RGB', (PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT), color='red')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        return image_bytes


layout = [
    [sg.Text("What's your name?")],
    [sg.Input(key="-INPUT-")],
    [sg.Text(size=(40, 1), key="-OUTPUT-")],
    [sg.Button("Random Image"), sg.Button("Quit")],
    [sg.Image(key="-PREVIEW-", size=(PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT))],
    [sg.Button(size=(40, 1), key="-IMG_NAME-")],
    [sg.Button(size=(100, 2), key="-IMG_DIR-")]
]

# Create the window
window = sg.Window("INDEXR", layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    print("event", event)
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == "Quit":
        break
    elif event == "-IMG_NAME-":
        subprocess.call(['open', "/Users/jayglickman/Library/CloudStorage/Dropbox/Pictures/Costume Album/2010_Inigo Montoya_1.jpg"])
    elif event == "-IMG_DIR-":
        print("in here")
        subprocess.call(['open', "/Users/jayglickman/Library/CloudStorage/Dropbox/Pictures/Costume Album"])
    # Output a message to the window
    elif event == "Random Image":
        query_class = TableQueries()
        random_row = query_class.get_random_image_ref()
        print("random row file--->", random_row)
        img_directory, img_name = split_path_and_file(random_row.get("file"))
        preview_img = load_image_from_path(random_row.get("file"))
        print("type-->", type(preview_img))
        print("image--->", preview_img)
        layout = [
            [sg.Text("What's your name?")],
            [sg.Input(key="-INPUT-")],
            [sg.Text(size=(40, 1), key="-OUTPUT-")],
            [sg.Button("Random Image"), sg.Button("Quit")],
            [sg.Image(preview_img, key='-IMAGE-')],
            [sg.Button("Load Image", size=(40, 1), key="-IMG_NAME-")],
            [sg.Text(size=(40, 1), key="-IMG_DIR")]
        ]
        window["-PREVIEW-"].update(
            data=preview_img.getvalue()
        )
        print("image name", img_name)
        print("image dire", img_directory)
        window["-IMG_NAME-"].update(img_name)
        window["-IMG_DIR-"].update(img_directory)

    window["-OUTPUT-"].update(
        "Hello " + values["-INPUT-"] + "! Thanks for trying PySimpleGUI"
    )

# Finish up by removing from the screen
window.close()
