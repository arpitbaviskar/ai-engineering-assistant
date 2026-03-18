# test_vision.py — run with: python test_vision.py
import requests
import urllib.request
import os
import json

API = "http://127.0.0.1:8000"

def download_test_image(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        print("Done.")
    return filename

def test_vision(image_path):
    print(f"\nTesting /vision with: {image_path}")
    print("-" * 50)
    with open(image_path, "rb") as f:
        ext = image_path.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
        response = requests.post(
            f"{API}/vision",
            files={"file": (os.path.basename(image_path), f, mime)}
        )
    if response.status_code == 200:
        data = response.json()
        print(f"Detections ({len(data['detections'])}):")
        for d in data["detections"]:
            print(f"  - {d['label']:20s} confidence: {d['confidence']:.1%}")
        print(f"\nDiagnosis:\n{data['diagnosis']}")
    else:
        print(f"ERROR {response.status_code}: {response.text}")

# --- Test images (YOLO works best on these) ---
test_images = [
    ("https://ultralytics.com/images/zidane.jpg",     "test_person.jpg"),
    ("https://ultralytics.com/images/bus.jpg",         "test_bus.jpg"),
]

for url, filename in test_images:
    path = download_test_image(url, filename)
    test_vision(path)