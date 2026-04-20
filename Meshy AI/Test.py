import json
import time
import requests
import base64

# 1. Convert your local image to Base64
local_file_path = "/Users/rosekoehler/Desktop/Research/Meshy/SpoonTest.jpg"

with open(local_file_path, "rb") as f:
    image_bytes = f.read()
    base64_str = base64.b64encode(image_bytes).decode("utf-8")

data_uri = f"data:image/jpeg;base64,{base64_str}"

# 2. Set payload for image-to-3D request
payload = {
    "image_url": data_uri,
    "enable_pbr": True,
    "should_remesh": True,
    "should_texture": True,
    "save_pre_remeshed_model": True
}

headers = {
    "Authorization": "Bearer REDACTED"
}

# 3. Create a 3D model from the image
response = requests.post(
    "https://api.meshy.ai/openapi/v1/image-to-3d",
    headers=headers,
    json=payload
)
response.raise_for_status()
task_id = response.json()["result"]
print("3D task created. Task ID:", task_id)

# 4. Poll the task status until it's done
while True:
    status_response = requests.get(
        f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}",
        headers=headers
    )
    status_response.raise_for_status()
    task_info = status_response.json()
    
    if task_info["status"] == "SUCCEEDED":
        print("3D model generation finished.")
        break

    print(f"Status: {task_info['status']} | Progress: {task_info.get('progress', 0)}% | Retrying in 5s...")
    time.sleep(5)

# 5. Download the 3D model in GLB format
model_url = task_info["model_urls"]["glb"]
model_response = requests.get(model_url)
model_response.raise_for_status()

with open("Spoon_model.glb", "wb") as f:
    f.write(model_response.content)

print("3D model downloaded as Spoon_model.glb")