import logging
import io
import PySimpleGUI as sg
from PIL import Image
import subprocess
import base64

from indexr.utils import get_tag_names_from_dict, load_creds_to_environ, split_path_and_file
from indexr.db.query_manipulation import TableQueries

load_creds_to_environ()

PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT = 400, 400


def load_image_from_path(file_path, resize_x=PREVIEW_IMG_WIDTH, resize_y=PREVIEW_IMG_HEIGHT):
    print("file path", file_path)
    try:
        with Image.open(file_path) as img:  # PIL solution
            logging.debug("exif", img.getexif())
            bio = io.BytesIO()
            cur_width, cur_height = img.size
            new_width, new_height = resize_x, resize_y
            scale = min(new_height/cur_height, new_width/cur_width)
            img = img.resize((int(cur_width*scale), int(cur_height*scale)))
            print("image --->", img)
            img.save(bio, format="PNG")
            return bio
    except Exception as e:
        logging.warning(f"load_image_from_path unable to load image {file_path}: {e}")
        # return default image
        image = Image.new('RGB', (PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT), color='red')
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='PNG')
        return image_bytes


def resize_image(image, resize_x, resize_y):
    print("image", image)
    try:
        with Image.open(io.BytesIO(base64.b64decode(image))) as img:
            logging.debug("exif", img.getexif)
            print("exif exif", img.getexif())
            bio = io.BytesIO()
            cur_width, cur_height = img.size
            new_width, new_height = resize_x, resize_y
            scale = min(new_height/cur_height, new_width/cur_width)
            img = img.resize((int(cur_width*scale), int(cur_height*scale)))
            print("img--->", img)
            img.save(bio, format="PNG")
            return bio
    except Exception as e:
        logging.warning(f"resize_image unable to load image {e}")


def resize_image_bytes(image_bytes, new_size, format=None):
    """
    Resizes an image represented as bytes.

    :param image_bytes: The original image in bytes.
    :param new_size: A tuple (width, height) representing the new size.
    :param format: Optional. The format to save the resized image. If None, it uses the original format.
    :return: The resized image in bytes.
    """
    # Create a BytesIO object from the original bytes
    with io.BytesIO(image_bytes) as input_buffer:
        with Image.open(input_buffer) as img:
            # Preserve the image's original format if not specified
            img_format = format if format else img.format

            # Resize the image
            resized_img = img.resize(new_size, Image.ANTIALIAS)

            # Save the resized image to a new BytesIO object
            with io.BytesIO() as output_buffer:
                resized_img.save(output_buffer, format=img_format)
                resized_bytes = output_buffer.getvalue()

    return resized_bytes


def update_tag_button(index, tag):
    # tab = sg.Col(
    #     [
    #         sg.B("X", border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()),
    #         k=('-DEL-', tag['id']), tooltip='Delete this item'),
    #         sg.B(tag['tag_name'], size=(10, 1), k=('-DESC-', tag['id'])),
    #     ]
    # )

    tab = [sg.pin(sg.Col([[sg.B("X", border_width=0, pad=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=(f'{index}-X', 5), tooltip='Delete this item'),
                            sg.B(f'{tag.get("tag_name")}', button_color=("white", "gray"), pad=0, k=('-STATUS-', 5))]], k=(f'{index}', 5)))]
    return tab


tag_count = 10
tags_row = []
# resized_x_mark = resize_image_bytes(sg.red_x, 50)
for tag_button_index in range(tag_count):
    tags_row.append(sg.Button(image_data=sg.red_x, image_subsample=2, button_color=sg.theme_background_color(), border_width=0, pad=0,
        key=f"{tag_button_index}-X", tooltip='Delete this tag', visible=False))
    tags_row.append(sg.Button(f"{tag_button_index}", pad=0, key=tag_button_index, visible=False))
tag_col = [
    sg.Column(
        [
            tags_row
        ],
        expand_x=True
    )
]

layout = [
    [sg.Text("What's your name?")],
    [sg.Text(size=(40, 1), key="-OUTPUT-")],
    [sg.Button("Random Image"), sg.Button("Quit")],
    [sg.Image(key="-PREVIEW-", size=(PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT))],
    [sg.Input(size=(40, 1), key="-NEW-TAGS-"), sg.Button("update tags", key="-UPDATE-TAGS-")],
    tag_col,
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
tag_buttons = []
image_tags = []
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
        tags = values["-NEW-TAGS-"].split(" ") if values["-NEW-TAGS-"] else []
        print("added tags are", tags)

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
        image_tags = []
        random_row = query_class.get_random_image_ref()
        if not random_row:
            continue
        image_tags = query_class.get_tags_for_image_id(random_row["id"])
        # for index, tag in enumerate(image_tags):
        #     tag_buttons.append(update_tag_button(index, tag))
        image_tag_names = get_tag_names_from_dict(image_tags)
        print("image tags", image_tags, image_tag_names)
        print("random row file--->", random_row)
        img_path = random_row.get("file")
        img_directory, img_name = split_path_and_file(img_path)
        preview_img = load_image_from_path(img_path)
        print("tag_buttons", tag_buttons)
        layout = [
            [sg.Text("Behold!")],
            [sg.Text(size=(40, 1), key="-OUTPUT-")],
            [sg.Button("Random Image"), sg.Button("Quit")],
            [sg.Image(preview_img, key='-IMAGE-')],
            [sg.Input(size=(25, 1), key="-NEW-TAGS-")],
            tag_col,
            [sg.Button("Load Image", size=(40, 1), key="-IMG_NAME-")],
            [sg.Text(size=(40, 1), key="-IMG_DIR-")]
        ]
        window["-PREVIEW-"].update(
            data=preview_img.getvalue()
        )
        window["-IMG_NAME-"].update(img_name)
        window["-IMG_DIR-"].update(img_directory)
        window["-UPDATE-TAGS-"].update("Update Tags")
        # cleanup old tags before showing new:
        for index in range(tag_count):
            window[f"{index}-X"].update(visible=False)
            window[index].update(visible=False)
        for index, tag in enumerate(image_tags):
            window[f"{index}-X"].update(visible=True)
            window[index].update(tag.get("tag_name"), visible=True)
        for tag_button in tag_buttons:
            window.extend_layout(window['-TAGS-'], [tag_button])
