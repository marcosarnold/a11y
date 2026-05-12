import requests
import base64
import time

API_KEY = "REDACTED"

# CHANGE THIS TO YOUR PATH
image_path = "/Users/rosekoehler/Desktop/spoonTest2.png"

with open(image_path, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")


payload = {
    "ai_model": "nano-banana",
    "prompt": "Make the handle smaller",
    "reference_image_urls": [
        f"data:image/jpeg;base64,{encoded}"
    ]
}

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.post(
    "https://api.meshy.ai/openapi/v1/image-to-image",
    headers=headers,
    json=payload,
)

response.raise_for_status()
data = response.json()

print("Create response:", data)

task_id = data["result"]
print("Task ID:", task_id)


final_data = None

while True:
    r = requests.get(
        f"https://api.meshy.ai/openapi/v1/image-to-image/{task_id}",
        headers=headers
    )

    r.raise_for_status()
    final_data = r.json()

    print("Status:", final_data["status"])

    if final_data["status"] == "SUCCEEDED":
        break

    if final_data["status"] in ["FAILED", "CANCELED"]:
        print("Task failed:", final_data)
        exit()

    time.sleep(2)

#getting image url
image_url = final_data["image_urls"][0]
print("IMAGE URL:", image_url)

#download image
img_data = requests.get(image_url).content

with open("output3.png", "wb") as f:
    f.write(img_data)

print("Saved as output3.png")

### Turning this into a 3D 

# 2. Set payload for image-to-3D request
payload = {
    "image_url": final_data["image_urls"][0],
    "enable_pbr": True,
    "should_remesh": True,
    "should_texture": True,
    "save_pre_remeshed_model": True
}

headers = {
    "Authorization": "Bearer REDACTED"
}

response = requests.post(
    "https://api.meshy.ai/openapi/v1/image-to-3d",
    headers=headers,
    json=payload
)
response.raise_for_status()
task_id = response.json()["result"]
print("3D task created. Task ID:", task_id)


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

model_url = task_info["model_urls"]["glb"]
model_response = requests.get(model_url)
model_response.raise_for_status()

with open("IterativeTest3Small.glb", "wb") as f:
    f.write(model_response.content)

print("3D model downloaded as IterativeTest3Small.glb")
