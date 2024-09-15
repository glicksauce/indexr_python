import logging
import io
import PySimpleGUI as sg
from PIL import Image
import subprocess

from indexr.utils import get_tag_names_from_dict, load_creds_to_environ, split_path_and_file
from indexr.db.query_manipulation import TableQueries

load_creds_to_environ()

PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT = 400, 400


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
    [sg.Text(size=(40, 1), key="-OUTPUT-")],
    [sg.Button("Random Image"), sg.Button("Quit")],
    [sg.Image(key="-PREVIEW-", size=(PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT))],
    [sg.Input(key="-TAGS-"), sg.Button(key="-UPDATE-TAGS-")],
    [sg.Button(size=(40, 1), key="-IMG_NAME-")],
    [sg.Button(size=(100, 2), key="-IMG_DIR-")]
]

# Create the window
window = sg.Window("INDEXR", layout)

img_path = None
img_directory = None
random_row = {
    "id": None
}
query_class = TableQueries()
# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    print("event", event)
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == "Quit":
        break
    elif event == "-IMG_NAME-":
        if img_path:
            subprocess.call(['open', img_path])
    elif event == "-IMG_DIR-":
        if img_directory:
            subprocess.call(['open', img_directory])
    elif event == "-UPDATE-TAGS-":
        tags = values["-TAGS-"].split(" ") if values["-TAGS-"] else []
        print("tags are", tags)

        created_tag_ids = []
        for tag in tags:
            res = query_class.create_tag(
                {
                    "tag_type": "user",
                    "tag_name": tag
                }
            )
            if res:
                created_tag_ids.append(res)
        print("created tag ids", created_tag_ids)
        for tag_id in created_tag_ids:
            res = query_class.assign_tag_to_file(tag_id, random_row["id"])
            print("assign_tag_to_file", res)
    # Output a message to the window
    elif event == "Random Image":
        random_row = query_class.get_random_image_ref()
        if not random_row:
            continue
        image_tags = query_class.get_tags_for_image_id(random_row["id"])
        image_tag_names = get_tag_names_from_dict(image_tags)
        print("image tags", image_tags, image_tag_names)
        print("random row file--->", random_row)
        img_path = random_row.get("file")
        img_directory, img_name = split_path_and_file(img_path)
        preview_img = load_image_from_path(img_path)
        print("type-->", type(preview_img))
        print("image--->", preview_img)
        layout = [
            [sg.Text("Behold!")],
            [sg.Text(size=(40, 1), key="-OUTPUT-")],
            [sg.Button("Random Image"), sg.Button("Quit")],
            [sg.Image(preview_img, key='-IMAGE-')],
            [sg.Input(key="-TAGS-"), sg.Button(key="-UPDATE-TAGS-")],
            [sg.Button("Load Image", size=(40, 1), key="-IMG_NAME-")],
            [sg.Text(size=(40, 1), key="-IMG_DIR-")]
        ]
        window["-PREVIEW-"].update(
            data=preview_img.getvalue()
        )
        print("image path", img_path)
        print("image dire", img_directory)
        window["-IMG_NAME-"].update(img_name)
        window["-IMG_DIR-"].update(img_directory)
        window["-UPDATE-TAGS-"].update("Update Tags")
        window["-TAGS-"].update(' '.join(image_tag_names))

    # window["-OUTPUT-"].update(
    #     "Hello " + values["-TAGS-"] + "! Thanks for trying PySimpleGUI"
    # )

# Finish up by removing from the screen
window.close()
