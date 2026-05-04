import requests
import time

API_KEY = "REDACTED"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

#
# TEXT → 3D
#

prompt = """
A chunky ergonomic pencil grip for assistive writing.
It should be smooth, rounded, and easy to hold.
It should have a cylindrical hole through the center for a pencil.
It should have three shallow finger grooves on the outside.
The design should be simple, printable, and suitable for children or people with limited hand strength.
The design must fit a standard Ticonderoga No. 2 pencil, which has a diameter of approximately 7mm.
"""

payload = {
    "mode": "preview",
    "prompt": prompt,
    "art_style": "realistic",
    "should_remesh": True
}

response = requests.post(
    "https://api.meshy.ai/openapi/v2/text-to-3d",
    headers=headers,
    json=payload,
)
response.raise_for_status()

print("Submitted text-to-3D preview job.")
text3d_task_id = response.json()["result"]

#
# POLL FOR STATUS
#

while True:
    status_response = requests.get(
        f"https://api.meshy.ai/openapi/v2/text-to-3d/{text3d_task_id}",
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

filename = "Pencil_grip_text_to_3d1.stl"

with open(filename, "wb") as f:
    f.write(model_response.content)

print(f"3D model downloaded as {filename}")