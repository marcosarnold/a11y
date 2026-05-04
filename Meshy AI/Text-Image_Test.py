import requests
import json
import time

#
# TEXT-IMAGE    
#

payload = {
    "ai_model": "nano-banana",
    "prompt": "A 3D printable pencil grip that can fit in a Ticonderoga No. 2 pencil and is designed for individuals with limited hand strength and mobility. Do not include the pencil in the final design.",
    "aspect_ratio": "16:9"
}
headers = {
    "Authorization": f"Bearer REDACTED"
}

response = requests.post(
    "https://api.meshy.ai/openapi/v1/text-to-image",
    headers=headers,
    json=payload,
)
response.raise_for_status()
print(response.json())

# retreive that text to image ID

task_id = response.json()["result"]

headers = {
    "Authorization": f"Bearer REDACTED"
}

response = requests.get(
    f"https://api.meshy.ai/openapi/v1/text-to-image/{task_id}",
    headers=headers,
)
response.raise_for_status()
print(response.json())

# stream the text to image

headers = {
    "Authorization": f"Bearer REDACTED",
    "Accept": "text/event-stream"
}

response = requests.get(
    f"https://api.meshy.ai/openapi/v1/text-to-image/{task_id}/stream",
    headers=headers,
    stream=True
)

for line in response.iter_lines():
    if line:
        if line.startswith(b'data:'):
            data = json.loads(line.decode('utf-8')[5:])
            print(data)
            # retrieve the image url
            if data.get('status') == 'SUCCEEDED':
                image_url = data["image_urls"][0]   
                print(f"image url is: {image_url}")
                break

            if data['status'] in ['SUCCEEDED', 'FAILED', 'CANCELED']:
                break

# retrieve the image url

response.close()

#
# IMAGE-3D   
#


payload = {
     # Using data URI example
     # image_url: f'data:image/png;base64,{YOUR_BASE64_ENCODED_IMAGE_DATA}',
    "image_url": image_url,
    "enable_pbr": True,
    "should_remesh": True,
    "should_texture": True,
    "save_pre_remeshed_model": True
}
headers = {
    "Authorization": f"Bearer REDACTED"
}

response = requests.post(
    "https://api.meshy.ai/openapi/v1/image-to-3d",
    headers=headers,
    json=payload,
)
response.raise_for_status()
print(response.json())


# retrieve image to 3d task
im3d_task_id = response.json()["result"]

while True:
    status_response = requests.get(
        f"https://api.meshy.ai/openapi/v1/image-to-3d/{im3d_task_id}",
        headers=headers
    )
    status_response.raise_for_status()
    task_info = status_response.json()
    
    if task_info["status"] == "SUCCEEDED":
        print("3D model generation finished.")
        break

    print(f"Status: {task_info['status']} | Progress: {task_info.get('progress', 0)}% | Retrying in 5s...")
    time.sleep(5)


model_url = task_info["model_urls"]["stl"]
model_response = requests.get(model_url)
model_response.raise_for_status()

with open("Pencil_grip3.stl", "wb") as f:
    f.write(model_response.content)

print("3D model downloaded as Pencil_grip3.stl")









