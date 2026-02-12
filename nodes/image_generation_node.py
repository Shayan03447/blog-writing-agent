from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import io
from pathlib import Path
from state.State import Blog_State
import re
import time
from datetime import datetime
from threading import Thread
import queue
import threading




_pipeline=None
_lock=threading.Lock()

def _get_pipeline():
    """Load Stable Diffusion model - optimized for CPU"""
    global _pipeline

    if _pipeline is not None:
        return _pipeline
    with _lock:
        if _pipeline is None:
            print("[INFO] Loading Stable Diffusion model (first time ~4GB download)...")
            _pipeline=StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32
            )
            _pipeline=_pipeline.to("cpu")
            # Memory optimizations for CPU
            try:
                _pipeline.enable_attention_slicing()
                _pipeline.enable_sequential_cpu_offload()
            except:
                pass
            print("[INFO] Model loaded successfully!")
    return _pipeline


# _pipeline=None
# def _get_pipeline():
#     """Load Stable Diffusion model - optimized for CPU"""
#     global _pipeline
#     if _pipeline is None:
#         print("[INFO] Loading Stable Diffusion model (first time ~4GB download)...")
#         _pipeline=StableDiffusionPipeline.from_pretrained(
#             "runwayml/stable-diffusion-v1-5",
#             torch_dtype=torch.float32
#         )
#         _pipeline=_pipeline.to("cpu")
        
#         # Memory optimizations for CPU
#         try:
#             _pipeline.enable_attention_slicing()  # Reduces memory usage
#             _pipeline.enable_sequential_cpu_offload()  # Memory efficient
#         except:
#             pass
#         print("[INFO] Model loaded successfully!")
#     return _pipeline

def _stable_diffusion_generate_image_bytes(prompt: str, width: int=512, height: int=512, timeout_seconds: int=10)->bytes:
    """
    Generate an image from stable diffusion and return bytes.
    If generation takes longer than timeout_seconds, raises TimeoutError.
    """
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🎨 Starting image generation...")
    print(f"   📝 Prompt: {prompt[:60]}...")
    print(f"   📐 Size: {width}x{height}")
    print(f"   ⏱️  Time limit: {timeout_seconds} seconds")
    print(f"   ⏳ Generating... (this may take time)\n")
    
    pipeline=_get_pipeline()
    start_time = time.time()
    
    # Result queue for thread communication
    result_queue = queue.Queue()
    error_queue = queue.Queue()
    
    def generate_in_thread():
        """Generate image in separate thread"""
        try:
            image = pipeline(
                prompt=prompt,
                num_inference_steps=20,  # Reduced for speed
                width=width,
                height=height,
                guidance_scale=7.5
            ).images[0]
            
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            result_queue.put(img_bytes.getvalue())
        except Exception as e:
            error_queue.put(e)
    
    # Start generation in thread
    thread = Thread(target=generate_in_thread, daemon=True)
    thread.start()
    
    # Wait for result with timeout
    elapsed = 0
    last_progress_time = 0
    while elapsed < timeout_seconds:
        if not result_queue.empty():
            img_bytes = result_queue.get()
            elapsed = time.time() - start_time
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Image generated successfully in {elapsed:.1f} seconds\n")
            return img_bytes
        
        if not error_queue.empty():
            error = error_queue.get()
            raise error
        
        # Progress indicator - print every 2 seconds
        elapsed = time.time() - start_time
        if int(elapsed) != int(last_progress_time) and int(elapsed) % 2 == 0 and elapsed < timeout_seconds - 1:
            remaining = timeout_seconds - elapsed
            print(f"   ⏳ Still generating... ({elapsed:.1f}s elapsed, {remaining:.1f}s remaining)")
            last_progress_time = elapsed
        
        time.sleep(0.5)  # Check every 0.5 seconds
    
    # Timeout reached
    elapsed = time.time() - start_time
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏱️  Timeout! Generation took {elapsed:.1f} seconds (> {timeout_seconds}s limit)\n")
    raise TimeoutError(f"Image generation exceeded {timeout_seconds} seconds timeout")

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

    total_images = len(image_specs)
    print(f"\n{'='*60}")
    print(f"📸 Processing {total_images} image(s)...")
    print(f"{'='*60}\n")
    
    for idx, spec in enumerate(image_specs, 1):
        placeholder=spec.get("placeholders") or ""
        filename=spec["filename"]
        out_path=images_dir/filename
        
        print(f"[{idx}/{total_images}] Processing: {filename}")

        if not out_path.exists():
            try:
                size_str=spec.get("size","1024*1024")
                width, height=map(int, size_str.split("*"))
                
                # Force smaller size for faster generation (CPU optimization)
                if width > 512 or height > 512:
                    print(f"   ⚠️  Size reduced from {width}x{height} to 512x512 for faster generation")
                    width, height = 512, 512

                # Generate with 10 second timeout
                img_bytes=_stable_diffusion_generate_image_bytes(
                    prompt=spec["prompt"],
                    width=width,
                    height=height,
                    timeout_seconds=10
                )
                out_path.write_bytes(img_bytes)
                print(f"   ✅ Image saved: {filename}\n")
                
            except TimeoutError:
                # Timeout case - use simple markdown fallback
                print(f"   ⏱️  Timeout reached - using fallback markdown\n")
                fallback_md = (
                    f"**{spec.get('caption', spec.get('alt', 'Image'))}**\n\n"
                    f"*Image generation is in progress. The diagram for '{spec.get('caption', 'this section')}' "
                    f"will be available shortly.*\n"
                )
                md=md.replace(placeholder, fallback_md)
                continue
                
            except Exception as e:
                # Other errors - use error block
                print(f"   ❌ Error: {str(e)}\n")
                prompt_block=(
                    f"> **[IMAGE GENERATION FAILED]** {spec.get('caption','')}\n>\n"
                    f"> **Alt:** {spec.get('alt','')}\n>\n"
                    f"> **Prompt:** {spec.get('prompt','')}\n>\n"
                    f"> **Error:** {str(e)}\n"
                )
                md=md.replace(placeholder, prompt_block)
                continue
        else:
            print(f"   ⏭️  Image already exists, skipping generation\n")
        
        # Success case - add image link
        img_md=f"![{spec['alt']}](images/{filename})\n*{spec['caption']}*"
        md=md.replace(placeholder, img_md)
    filename=f"{_safe_slug(plan.blog_title)}.md"
    Path(filename).write_text(md, encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"✅ Final blog saved: {filename}")
    print(f"{'='*60}\n")
    return {"final":md}

