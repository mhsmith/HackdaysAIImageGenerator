import io

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from .model import new_image, normalize_image


IMAGE_SIZE = 600


class InstructPix2Pix(toga.App):

    def startup(self):
        self.image = None

        self.filename_label = toga.Label("", style=Pack(flex=1))
        file_input = toga.Box(
            style=Pack(direction=ROW),
            children=[
                toga.Button("Choose file", on_press=self.on_choose_file),
                self.filename_label,
            ]
        )

        self.conversation = toga.ScrollContainer(
            style=Pack(flex=1),
            content=toga.Box(style=Pack(direction=COLUMN)),
        )

        self.img_guidance = self.labeled_slider(
            "Image guidance scale", range=(1, 10), value=1.5, tick_step=0.5, dp=1
        )
        self.guidance = self.labeled_slider(
            "Guidance scale", range=(1, 10), value=7, tick_step=0.5, dp=1
        )
        self.steps = self.labeled_slider(
            "Inference steps", range=(1, 100), value=20, tick_step=1, dp=0
        )
        self.prompt = toga.MultilineTextInput(
            placeholder="Enter image editing instruction here..."
        )
        widgets = toga.Box(
            style=Pack(direction=ROW),
            children=[
                toga.Box(
                    style=Pack(flex=1, direction=COLUMN),
                    children=[
                        self.prompt,
                        toga.Button("Run!", on_press=self.on_run),
                    ]
                ),
                toga.Box(
                    style=Pack(flex=1, direction=COLUMN),
                    children=[self.img_guidance, self.guidance, self.steps],
                )
            ]
        )

        main_box = toga.Box(
            style=Pack(direction=COLUMN),
            children=[
                toga.Label(
                    "\U0001F60A Choose an image file and start editing!",
                    style=Pack(font_weight="bold", font_size=20),
                ),
                file_input,
                self.conversation,
                widgets,
            ]
        )

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def labeled_slider(self, text, *, range, value, tick_step, dp):
        def on_change(slider):
            label.text = f"{text}: {slider.value:.{dp}f}"

        label = toga.Label("")
        slider = toga.Slider(range=range, value=value, on_change=on_change)
        on_change(slider)
        box = toga.Box(style=Pack(direction=COLUMN), children=[label, slider])
        box.slider = slider
        return box

    async def on_choose_file(self, button):
        filename = await self.main_window.open_file_dialog("Choose file")
        if filename:
            self.filename_label.text = str(filename)
            self.conversation.content.remove(*self.conversation.content.children.copy())
            with open(filename, "rb") as f:
                self.image = normalize_image(f.read(), IMAGE_SIZE)
                self.add_image("", self.image)

    def on_run(self, button):
        prompt_text = str(self.prompt.value)
        if self.image and prompt_text:
            self.prompt.value = ""
            self.image = new_image(
                prompt_text,
                self.image,
                self.img_guidance.slider.value,
                self.guidance.slider.value,
                int(self.steps.slider.value)
            )
            self.add_image(prompt_text, self.image)

    def add_image(self, text, pil_image):
        if text:
            self.conversation.content.add(toga.Label(text))

        f = io.BytesIO()
        pil_image.save(f, "png")
        self.conversation.content.add(
            toga.ImageView(
                toga.Image(data=f.getvalue()),
                style=Pack(width=pil_image.width, height=pil_image.height),
            )
        )


def main():
    return InstructPix2Pix()
