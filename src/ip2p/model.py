import io

import PIL.Image


def normalize_image(value, width):
    """
    normalize image to RBG channels and to the same size
    """
    b = io.BytesIO(value)
    image = PIL.Image.open(b).convert("RGB")
    aspect = image.size[1] / image.size[0]
    height = int(aspect * width)
    return image.resize((width, height), PIL.Image.LANCZOS)


def new_image(prompt, image, img_guidance, guidance, steps, width=600):
    """
    create a new image from the StableDiffusionInstructPix2PixPipeline model
    """
    return image  # TODO
