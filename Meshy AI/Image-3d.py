import requests
import time

# image URL
image_url = "https://www.makersmakingchange.com/sfsites/c/cms/delivery/media/MCWS2XVC6XFNCOLIQVLGRVMKZH74?version=1.1&channelId=0apJR0000000FNF"

API_KEY = "REDACTED"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

#
# IMAGE → 3D
#

payload = {
    "image_url": image_url,
    "enable_pbr": True,
    "should_remesh": True,
    "should_texture": True,
    "save_pre_remeshed_model": True
}

response = requests.post(
    "https://api.meshy.ai/openapi/v1/image-to-3d",
    headers=headers,
    json=payload,
)
response.raise_for_status()

print("Submitted image-to-3D job.")
im3d_task_id = response.json()["result"]

#
# POLL FOR STATUS
#

while True:
    status_response = requests.get(
        f"https://api.meshy.ai/openapi/v1/image-to-3d/{im3d_task_id}",
        headers=headers
    )
    status_response.raise_for_status()
    task_info = status_response.json()

    status = task_info["status"]
    progress = task_info.get("progress", 0)

    print(f"Status: {status} | Progress: {progress}%")

    if status == "SUCCEEDED":
        print("3D model generation finished.")
        break
    elif status in ["FAILED", "CANCELED"]:
        raise Exception(f"Task ended with status: {status}")

    time.sleep(5)

#
# DOWNLOAD STL
#

model_url = task_info["model_urls"]["stl"]
model_response = requests.get(model_url)
model_response.raise_for_status()

with open("Pencil_grip3.stl", "wb") as f:
    f.write(model_response.content)

print("3D model downloaded as fork_grip.stl")
