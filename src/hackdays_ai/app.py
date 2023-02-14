import io
import multiprocessing
from shutil import rmtree
from threading import Thread

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from .model import MODEL_DIR, load_model, new_image


MIN_RESOLUTION = 256
MAX_RESOLUTION = 512

PADDING = 8
DESCRIPTION_FONT_SIZE = 15
CAPTION_STYLE = Pack(text_align="center", padding=PADDING)


class HackdaysAIApp(toga.App):

    def startup(self):
        self.commands.add(
            toga.Command(self.delete_model, "Delete model files", group=toga.Group.APP)
        )

        main_box = toga.Box(
            style=Pack(direction=COLUMN),
            children=[
                toga.Box(style=Pack(flex=1)),
                toga.Label(
                    "Downloading model files: these are about 5 GB so please be patient.\n"
                    "You can delete them later using the menu above."
                    if not MODEL_DIR.exists()
                    else "Loading model",
                    style=CAPTION_STYLE),
                toga.Box(style=Pack(flex=1))
            ],
        )

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
        Thread(target=self.load_model).start()

    def load_model(self):
        load_model()
        self.add_background_task(self.on_model_loaded)

    def delete_model(self, _):
        if MODEL_DIR.exists():
            rmtree(MODEL_DIR)

    def on_model_loaded(self, _):
        self.conversation = toga.Box(style=Pack(direction=COLUMN, padding=PADDING))

        self.resolution = self.labeled_slider(
            "Resolution", range=(MIN_RESOLUTION, MAX_RESOLUTION), value=MAX_RESOLUTION,
            tick_step=16,
        )
        self.guidance = self.labeled_slider(
            "Guidance scale", range=(1, 10), value=7.5, tick_step=0.5
        )
        self.steps = self.labeled_slider(
            "Inference steps", range=(1, 30), value=10, tick_step=1
        )
        self.prompt = toga.MultilineTextInput(
            style=Pack(font_size=DESCRIPTION_FONT_SIZE, flex=1, padding_bottom=PADDING),
            placeholder="Enter image description here..."
        )
        widgets = toga.Box(
            style=Pack(direction=ROW, padding_left=PADDING),
            children=[
                toga.Box(
                    style=Pack(flex=1, direction=COLUMN, padding_right=PADDING),
                    children=[
                        self.prompt,
                        toga.Button(
                            "Run!",
                            style=Pack(padding_bottom=PADDING),
                            on_press=self.on_run
                        ),
                    ]
                ),
                toga.Box(
                    style=Pack(flex=1, direction=COLUMN, padding_right=PADDING),
                    children=[self.resolution, self.guidance, self.steps],
                )
            ]
        )

        main_box = toga.Box(
            style=Pack(direction=COLUMN),
            children=[
                toga.Label("To visit this app's GitHub page, or delete the model files, "
                           "use the menus above.\n"
                           "A black image means the NSFW filter has been triggered.",
                           style=CAPTION_STYLE),
                toga.ScrollContainer(
                    style=Pack(flex=1, padding_bottom=PADDING),
                    content=self.conversation
                ),
                widgets,
            ]
        )
        self.main_window.content = main_box

    def labeled_slider(self, text, *, range, value, tick_step):
        def on_change(slider):
            dp = 0 if isinstance(tick_step, int) else 1
            label.text = f"{text}: {slider.value:.{dp}f}"

        label = toga.Label("")
        slider = toga.Slider(
            range=range, value=value,
            tick_count=round((range[1] - range[0]) / tick_step) + 1,
            on_change=on_change,
        )
        on_change(slider)
        box = toga.Box(
            style=Pack(direction=COLUMN, padding_bottom=PADDING),
            children=[label, slider],
        )
        box.slider = slider
        return box

    def on_run(self, button):
        prompt_text = str(self.prompt.value)
        if prompt_text:
            kwargs = dict(
                resolution=int(self.resolution.slider.value),
                guidance=self.guidance.slider.value,
                steps=int(self.steps.slider.value),
            )
            pil_image = new_image(prompt_text, **kwargs)
            self.add_image(f"{prompt_text} {kwargs}", pil_image)

    def add_image(self, text, pil_image):
        if text:
            self.conversation.add(
                toga.Label(
                    text,
                    style=Pack(font_size=DESCRIPTION_FONT_SIZE, padding_bottom=PADDING)
                )
            )

        f = io.BytesIO()
        pil_image.save(f, "png")
        self.conversation.add(
            toga.ImageView(
                toga.Image(data=f.getvalue()),
                style=Pack(
                    width=MAX_RESOLUTION, height=MAX_RESOLUTION, padding_bottom=PADDING
                ),
            )
        )


def main():
    # https://github.com/beeware/briefcase-macOS-app-template/issues/7
    multiprocessing.set_start_method("fork")

    return HackdaysAIApp()
