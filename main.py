import os
import json
import time
import io
import base64
from PIL import Image
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

# make the OpenAI client available to other modules
# expects OPENAI_API_KEY to be set in environment (e.g. via .env)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# helper to read blog titles from JSON

def load_titles(path="titles.json"):
    """Return list of title entries from the given JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_prompts(path="prompts.json"):
    """Return dict of prompt templates from JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def generate_images_for_titles(
    titles,
    prompt_type,
    prompt_templates,
    model="gpt-image-1",
    size="1024x1024",
    delay=0.3,
    save_dir=None,
):
    """Generate images for a list of title dicts using the OpenAI Images API.

    The implementation follows the current OpenAI SDK pattern shown in the
    user's reference snippet:

        result = client.images.generate(
            model="gpt-image-1",
            prompt="simple sketch of a cat",
            size="256x256",
            n=1
        )

    The encoded image is returned in ``result.data[0].b64_json`` and must be
    base64-decoded before opening with ``PIL.Image``.

    Args:
        titles: iterable of dicts containing a 'title' key.
        prompt_type: key to select template from ``prompt_templates``.
        prompt_templates: mapping of prompt_type -> template string.
        model: OpenAI image model to pass to client (default ``gpt-image-1``).
        size: output image dimensions (e.g. "256x256" or "512x512").
        delay: seconds to sleep between requests.
        save_dir: if provided, images will also be saved into this directory.

    Returns:
        List of tuples (PIL.Image, title_str, filename) for each generated image.
    """
    if prompt_type not in prompt_templates:
        raise ValueError(f"Prompt type '{prompt_type}' not found in templates")

    template = prompt_templates[prompt_type]
    results = []

    # ensure save directory exists if requested
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    for idx, entry in enumerate(titles, start=1):
        title_str = entry.get("title", "")
        prompt = template.format(blog_title=title_str)

        result = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            n=1,
        )
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        pil_image = Image.open(io.BytesIO(image_bytes))

        filename = f"{prompt_type}_image_{idx}.png"
        if save_dir:
            path = os.path.join(save_dir, filename)
            pil_image.save(path)
        results.append((pil_image, title_str, filename))

        time.sleep(delay)

    return results


# keep original script behaviour when run directly
if __name__ == "__main__":
    # ensure output directory exists
    os.makedirs("images", exist_ok=True)

    titles = load_titles()
    prompt_templates = load_prompts()
    prompt_type = "modern_infographic"

    generated = generate_images_for_titles(
        titles[:10], prompt_type, prompt_templates, save_dir="images"
    )
    for img, title, fname in generated:
        print(f"Saved image for '{title}' as {fname}")