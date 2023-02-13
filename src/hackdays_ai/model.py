
import torch
from diffusers import DPMSolverMultistepScheduler, StableDiffusionPipeline


model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)

device = (
    torch.device('mps') if torch.backends.mps.is_available()
    else torch.device('cuda') if torch.cuda.is_available()
    else 'cpu'
)
pipe = pipe.to(device)
pipe.enable_attention_slicing()
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)


def new_image(prompt, resolution, guidance, steps):
    return pipe(
        prompt,
        width=resolution, height=resolution,
        guidance_scale=guidance, num_inference_steps=steps,
    ).images[0]
