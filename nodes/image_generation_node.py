from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import io
from pathlib import Path
from state.State import Blog_State
import re

_pipeline=None
def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline=StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32
        )
        _pipeline=_pipeline.to("cpu")
    return _pipeline

def _stable_diffusion_generate_image_bytes(prompt: str, width: int=512, height: int=512)->bytes:
    """Generate an image from stable diffusion and return bytes"""
    pipeline=_get_pipeline()
    image=pipeline(
        prompt=prompt,
        num_inference_steps=25,
        width=width,
        height=height,
        guidance_scale=7.5
    ).images[0]
    img_bytes=io.BytesIO()
    image.save(img_bytes, format="PNG")
    return img_bytes.getvalue()

def _safe_slug(title: str)-> str:
    s= title.strip().lower()
    s=re.sub(r"[^a-z0-9 _-]+", "", s)
    s=re.sub(r"\s+","_",s).strip("_")
    return s or "blog"

def generate_and_place_images(state: Blog_State)-> dict:
    plan=state["plan"]
    assert plan is not None
    md=state.get("md_with_placeholders") or state["merged_md"]
    image_specs=state.get("image_specs", []) or []

    if not image_specs:
        filename=f"{_safe_slug(plan.blog_title)}.md"
        Path(filename).write_text(md, encoding="utf-8")
        return {"final": md}

    images_dir=Path("images")
    images_dir.mkdir(exist_ok=True)

    for spec in image_specs:
        placeholder=spec.get("placeholders", spec.get("placeholders", ""))
        filename=spec["filename"]
        out_path=images_dir/filename

        if not out_path.exists():
            try:
                size_str=spec.get("size","1024*1024")
                width, height=map(int, size_str.split("*"))

                img_bytes=_stable_diffusion_generate_image_bytes(
                    prompt=spec["prompt"],
                    width=width,
                    height=height
                )
                out_path.write_bytes(img_bytes)
            except Exception as e:
                prompt_block=(
                    f"> **[IMAGE GENERATION FAILED]**{spec.get('caption','')}\n>\n"
                    f"> **Alt:** {spec.get('alt','')}\n>\n"
                    f"> **Prompt:** {spec.get('prompt','')}\n>\n"
                    f"> **Error:** {str(e)}\n"
                )
                md=md.replace(placeholder, prompt_block)
                continue
        img_md=f"![{spec['alt']}](images/{filename})\n*{spec['caption']}*"
        md=md.replace(placeholder, img_md)
    filename=f"{_safe_slug(plan.blog_title)}.md"
    Path(filename).write_text(md, encoding="utf-8")
    return {"final":md}

