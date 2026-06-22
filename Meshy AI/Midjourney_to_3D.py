import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["MESHY_API_KEY"]
MESHY_BASE_URL = "https://api.meshy.ai/openapi/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Step 1: Generate image via Midjourney MCP in Claude Code, then paste the CDN URL here.
# Example prompt: "a photorealistic assistive utensil grip handle --ar 1:1 --no text, watermark"
MIDJOURNEY_IMAGE_URL = "PASTE_MIDJOURNEY_CDN_URL_HERE"

OUTPUT_NAME = "midjourney_test"


def create_image_to_3d(image_url: str) -> str:
    payload = {
        "image_url": image_url,
        "enable_pbr": True,
        "should_remesh": True,
        "should_texture": True,
        "save_pre_remeshed_model": True,
    }
    response = requests.post(
        f"{MESHY_BASE_URL}/image-to-3d",
        headers=HEADERS,
        json=payload,
    )
    response.raise_for_status()
    return response.json()["result"]


def poll_task(task_id: str, interval: int = 5) -> dict:
    while True:
        response = requests.get(
            f"{MESHY_BASE_URL}/image-to-3d/{task_id}",
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()
        status = data.get("status")
        progress = data.get("progress", 0)
        print(f"  {status} — {progress}%")

        if status == "SUCCEEDED":
            return data
        elif status in ("FAILED", "EXPIRED"):
            raise RuntimeError(f"Task {status}: {data.get('task_error', {})}")

        time.sleep(interval)


def download(url: str, path: str) -> None:
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print(f"  Saved → {path}")


def main():
    print(f"Source image: {MIDJOURNEY_IMAGE_URL}\n")

    print("Submitting to Meshy image-to-3d...")
    task_id = create_image_to_3d(MIDJOURNEY_IMAGE_URL)
    print(f"Task ID: {task_id}\n")

    print("Polling...")
    result = poll_task(task_id)

    for fmt, url in result.get("model_urls", {}).items():
        if url and fmt in ("glb", "obj", "stl"):
            download(url, f"{OUTPUT_NAME}.{fmt}")

    thumbnail = result.get("thumbnail_url")
    if thumbnail:
        download(thumbnail, f"{OUTPUT_NAME}_preview.png")

    print(f"\n--- Done ---")
    print(f"Midjourney image → Meshy 3D complete.")
    print(f"Compare with Meshy-only pipeline (Text-Image_Test.py) to evaluate quality.")


if __name__ == "__main__":
    main()
