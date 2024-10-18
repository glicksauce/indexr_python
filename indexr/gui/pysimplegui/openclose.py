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


class WindowPane:
    def __init__(
        self,
        width=600,
        height=600,
    ):
        self.width = width
        self.height = height
        self.tags_count = 10
        self.tags_row = self.build_tags_row()
        self.files_rows = self.build_files_row({})
        self.tags_column = self.build_tags_column(self.tags_row)
        self.files_column = self.build_files_column(self.files_rows)
        self.layout = self.initial_window_view()

    def build_tags_row(self):
        """
        builds a row of tags
        """
        tags_row = []
        for tag_button_index in range(self.tags_count):
            tags_row.append(sg.Button(image_data=sg.red_x, image_subsample=2, button_color=sg.theme_background_color(), border_width=0, pad=0,
                key=f"{tag_button_index}-X-", tooltip='Delete this tag', visible=False))
            tags_row.append(sg.Button(f"{tag_button_index}", pad=0, key=f"{tag_button_index}-TAG-", visible=False))
        return tags_row
    
    def build_files_row(self, rows):
        """
        :row dict[]:
        """
        res = []
        for row in rows:
            if row.get("file"):
                img_directory, img_name = split_path_and_file(row["file"])
            else:
                img_directory = ""
                img_name = ""
            res.append([img_directory, img_name, row])
        return res

    def update_tag_button(self, index, tag):
        tab = [sg.pin(sg.Col([[sg.B("X", border_width=0, pad=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), k=(f'{index}-X-'), tooltip='Delete this item'),
                                sg.B(f'{tag.get("tag_name")}', button_color=("white", "gray"), pad=0, k=('-STATUS-', 5))]], k=(f'{index}-TAG-')))]
        return tab

    def build_tags_column(self, rows: list):
        return [
            sg.Column(
                [
                    rows
                ],
                expand_x=True
            )
        ]

    def build_files_column(self, rows: list):
        # Table headings
        headings = ["Path", "File"]

        table = [
            sg.Table(
                values=rows,
                headings=headings,
                auto_size_columns=True,
                justification="right",
                enable_events=True,
                expand_x=True,
                expand_y=True,
                num_rows=5,
                key="-FILES-TABLE-"
            ),
        ]
        return [
            sg.Column(
                [
                    table
                ],
                expand_x=True
            )
        ]

    def initial_window_view(self):
        return [
            [
                sg.Col(
                    [
                        [sg.Text(size=(40, 1), key="-OUTPUT-")],
                        [sg.Button("Random Image"), sg.Button("Quit")],
                        [sg.Image(key="-PREVIEW-", size=(PREVIEW_IMG_WIDTH, PREVIEW_IMG_HEIGHT))],
                        [sg.Input(size=(40, 1), key="-NEW-TAGS-"), sg.Button("update tags", key="-UPDATE-TAGS-")],
                        self.tags_column,
                        [sg.Button(size=(40, 1), key="-IMG_NAME-")],
                        [sg.Button(size=(50, 2), key="-IMG_DIR-")]
                    ]
                ),
                self.files_column,
            ],
        ]

    def display_image_view(self, preview_img):
        self.layout = [
            [sg.Text(size=(40, 1), key="-OUTPUT-")],
            [sg.Button("Random Image"), sg.Button("Quit")],
            [sg.Image(preview_img, key='-IMAGE-')],
            [sg.Input(size=(25, 1), key="-NEW-TAGS-")],
            self.tags_column,
            [sg.Button("Load Image", size=(40, 1), key="-IMG_NAME-")],
            [sg.Text(size=(40, 1), key="-IMG_DIR-")],
            self.files_column,
        ]


def load_image_to_preview(file_row):
    image_tags = query_class.get_tags_for_image_id(file_row["id"])
    img_path = file_row.get("file")
    img_directory, img_name = split_path_and_file(img_path)
    preview_img = load_image_from_path(img_path)
    base_window.layout = base_window.display_image_view(preview_img)
    window["-PREVIEW-"].update(
        data=preview_img.getvalue()
    )
    window["-IMG_NAME-"].update(img_name)
    window["-IMG_DIR-"].update(img_directory)
    window["-UPDATE-TAGS-"].update("Update Tags")
    # cleanup old tags before showing new:
    for index in range(base_window.tags_count):
        window[f"{index}-X-"].update(visible=False)
        window[f"{index}-TAG-"].update(visible=False)
    for index, tag in enumerate(image_tags):
        window[f"{index}-X-"].update(visible=True)
        window[f"{index}-TAG-"].update(tag.get("tag_name"), visible=True)
        window[f"{index}-TAG-"].metadata = tag["id"]
    for tag_button in tag_buttons:
        window.extend_layout(window['-TAGS-'], [tag_button])


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


# Create the window
base_window = WindowPane()
window = sg.Window("INDEXR", base_window.layout)

img_path = None
img_directory = None
selected_files_row = {
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
            tag_id = query_class.create_tag(
                {
                    "tag_type": "user",
                    "tag_name": tag
                }
            )
            if tag_id:
                created_tag_ids.append(tag_id)
                new_tag = {"id": tag_id, "tag_name": tag}
                if new_tag not in image_tags:
                    print("appending", new_tag, " to image_tags")
                    image_tags.append(new_tag)
            added_tag_id = query_class.assign_tag_to_file(tag_id, selected_files_row["id"])
            print("assign_tag_to_file", added_tag_id)

        # update buttons without re-querying:
        # for index, tag in enumerate(image_tags):
        #     window[f"{index}-X-"].update(visible=True)
        #     window[f"{index}-TAG-"].update(tag.get("tag_name") + "-" + str(tag["id"]), visible=True)
        #     window[f"{index}-TAG-"].metadata = tag["id"]
        # for tag_button in tag_buttons:
        #     window.extend_layout(window['-TAGS-'], [tag_button])

        load_image_to_preview(selected_files_row)
    # Output a message to the window
    elif "-X-" in event:
        # DELETE TAG
        index = event.replace("-X-", "")
        print(f"index is:{index}:end")
        if not window[f"{index}-TAG-"].metadata:
            print("invalid tag skipping")
            continue
        print("about to remove tag", window[f"{index}-TAG-"].metadata)
        res = query_class.remove_tag_from_file(window[f"{index}-TAG-"].metadata)
        if res:
            window[f"{index}-X-"].update(visible=False)
            window[f"{index}-TAG-"].metadata = None
            window[f"{index}-TAG-"].update(visible=False)
        else:
            print("error: unable to delete")
    elif event == "Random Image":
        image_tags = []
        selected_files_row = query_class.get_random_image_ref()
        if not selected_files_row:
            continue
        load_image_to_preview(selected_files_row)
    elif "-TAG-" in event:
        button_index = event.replace("-TAG-", "")
        print(f"tag {button_index} clicked")
        tags_files_id = window[f"{button_index}-TAG-"]._metadata
        files_with_tag = query_class.get_files_from_tag(tags_files_id)
        print("files", files_with_tag)
        file_table_rows = base_window.build_files_row(files_with_tag)
        window["-FILES-TABLE-"].update(values=file_table_rows)
    elif "-FILES-TABLE-" in event:
        selected_file_index = values["-FILES-TABLE-"][0]
        print("file selected", file_table_rows[selected_file_index])
        load_image_to_preview(file_table_rows[selected_file_index][2])

