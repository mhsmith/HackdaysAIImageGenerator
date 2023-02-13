
from pathlib import Path

import torch
from diffusers import DPMSolverMultistepScheduler, StableDiffusionPipeline


MODEL_ID = "runwayml/stable-diffusion-v1-5"
MODEL_DIR = Path(
    f"~/.cache/huggingface/diffusers/models--{MODEL_ID.replace('/', '--')}"
).expanduser()


def load_model():
    device = (
        torch.device('mps') if torch.backends.mps.is_available()
        else torch.device('cuda') if torch.cuda.is_available()
        else 'cpu'
    )

    global pipe
    pipe = StableDiffusionPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.float16)
    pipe = pipe.to(device)
    pipe.enable_attention_slicing()
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)


def new_image(prompt, resolution, guidance, steps):
    return pipe(
        prompt,
        width=resolution, height=resolution,
        guidance_scale=guidance, num_inference_steps=steps,
    ).images[0]
